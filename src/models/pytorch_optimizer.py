"""
PyTorch-based optimization layer for fine-tuning clustering.
Uses differentiable soft clustering with Gumbel-Softmax.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple
from src.utils.data_structures import AssemblyPointCluster, BusZone
from src.utils.distance import batch_haversine_distance


class SoftClusteringOptimizer(nn.Module):
    """
    Differentiable soft clustering module for zone optimization.
    """
    
    def __init__(self,
                 n_zones: int,
                 feature_dim: int = 6,
                 bus_capacity: int = 20,
                 temperature: float = 1.0,
                 home_weight: float = 0.6,
                 school_weight: float = 0.4):
        """
        Initialize soft clustering optimizer.
        
        Args:
            n_zones: Number of bus zones
            feature_dim: Dimension of feature vectors
            bus_capacity: Maximum students per bus
            temperature: Temperature for Gumbel-Softmax (lower = harder assignments)
            home_weight: Weight for home proximity in loss
            school_weight: Weight for school proximity in loss
        """
        super().__init__()
        
        self.n_zones = n_zones
        self.bus_capacity = bus_capacity
        self.temperature = temperature
        self.home_weight = home_weight
        self.school_weight = school_weight
        
        # Learnable zone centroids
        self.zone_centroids = nn.Parameter(torch.randn(n_zones, feature_dim))
        
        # Learnable temperature (optional, for adaptive hardening)
        self.log_temperature = nn.Parameter(torch.log(torch.tensor(temperature)))
    
    def forward(self, features: torch.Tensor, weights: torch.Tensor) -> Tuple[torch.Tensor, dict]:
        """
        Perform soft clustering and compute loss.
        
        Args:
            features: Feature tensor (N, D) for N assembly points
            weights: Student counts (N,) for each assembly point
        
        Returns:
            Tuple of (soft_assignments, loss_dict)
            - soft_assignments: (N, K) soft assignment probabilities
            - loss_dict: Dictionary of loss components
        """
        # Compute distances from points to centroids
        home_features = features[:, :2]
        school_features = features[:, 2:4]
        centroid_home = self.zone_centroids[:, :2]
        centroid_school = self.zone_centroids[:, 2:4]
        
        home_distances = torch.cdist(home_features, centroid_home)
        school_distances = torch.cdist(school_features, centroid_school)
        
        # Normalize
        home_distances = home_distances / (home_distances.max() + 1e-6)
        school_distances = school_distances / (school_distances.max() + 1e-6)
        
        # Combined distance
        combined_distances = (self.home_weight * home_distances + 
                             self.school_weight * school_distances)
        
        # Convert distances to logits (negative distance = higher probability)
        logits = -combined_distances / torch.exp(self.log_temperature)
        
        # Gumbel-Softmax for differentiable soft assignments
        soft_assignments = F.gumbel_softmax(logits, tau=torch.exp(self.log_temperature), hard=False, dim=1)
        
        # Compute loss components
        loss_dict = self._compute_losses(soft_assignments, features, weights, combined_distances)
        
        return soft_assignments, loss_dict
    
    def _compute_losses(self, 
                       soft_assignments: torch.Tensor,
                       features: torch.Tensor,
                       weights: torch.Tensor,
                       distances: torch.Tensor) -> dict:
        """
        Compute multi-objective loss.
        
        Args:
            soft_assignments: Soft assignment probabilities (N, K)
            features: Feature tensor (N, D)
            weights: Student counts (N,)
            distances: Distance matrix (N, K)
        
        Returns:
            Dictionary of loss components
        """
        # 1. Distance loss (minimize total distance)
        distance_loss = (soft_assignments * distances).sum()
        
        # 2. Capacity constraint loss
        zone_loads = soft_assignments.T @ weights  # (K,) total students per zone
        capacity_violations = F.relu(zone_loads - self.bus_capacity)
        capacity_loss = capacity_violations.sum()
        
        # 3. Balance loss (encourage balanced zone sizes)
        target_load = weights.sum() / self.n_zones
        balance_loss = ((zone_loads - target_load) ** 2).mean()
        
        # 4. Compactness loss (minimize variance within zones)
        compactness_loss = self._compute_compactness(soft_assignments, features)
        
        # 5. School diversity loss (penalize many different schools per zone)
        school_diversity_loss = self._compute_school_diversity(soft_assignments, features)
        
        # Weighted total loss
        total_loss = (
            1.0 * distance_loss +
            100.0 * capacity_loss +  # High penalty for capacity violations
            0.5 * balance_loss +
            0.3 * compactness_loss +
            0.2 * school_diversity_loss
        )
        
        return {
            'total_loss': total_loss,
            'distance_loss': distance_loss.item(),
            'capacity_loss': capacity_loss.item(),
            'balance_loss': balance_loss.item(),
            'compactness_loss': compactness_loss.item(),
            'school_diversity_loss': school_diversity_loss.item(),
            'max_zone_load': zone_loads.max().item(),
            'min_zone_load': zone_loads.min().item()
        }
    
    def _compute_compactness(self, soft_assignments: torch.Tensor, features: torch.Tensor) -> torch.Tensor:
        """
        Compute within-cluster variance (compactness).
        
        Args:
            soft_assignments: (N, K)
            features: (N, D)
        
        Returns:
            Compactness loss scalar
        """
        # Compute weighted centroids for each zone
        weighted_features = soft_assignments.T @ features  # (K, D)
        assignment_sums = soft_assignments.sum(dim=0, keepdim=True).T  # (K, 1)
        centroids = weighted_features / (assignment_sums + 1e-6)
        
        # Compute variance
        compactness = 0.0
        for k in range(self.n_zones):
            # Weighted squared distance to centroid
            diff = features - centroids[k].unsqueeze(0)
            squared_dist = (diff ** 2).sum(dim=1)
            weighted_squared_dist = soft_assignments[:, k] * squared_dist
            compactness += weighted_squared_dist.sum()
        
        return compactness / self.n_zones
    
    def _compute_school_diversity(self, soft_assignments: torch.Tensor, features: torch.Tensor) -> torch.Tensor:
        """
        Penalize zones with high school diversity.
        
        Args:
            soft_assignments: (N, K)
            features: (N, D) - feature[i, 5] is school diversity count
        
        Returns:
            Diversity loss scalar
        """
        school_diversity = features[:, 5]  # Number of unique schools per assembly
        
        # Weighted average school diversity per zone
        zone_diversity = soft_assignments.T @ school_diversity  # (K,)
        
        # Penalize high diversity
        return zone_diversity.sum()
    
    def get_hard_assignments(self, soft_assignments: torch.Tensor) -> torch.Tensor:
        """
        Convert soft assignments to hard assignments.
        
        Args:
            soft_assignments: (N, K) soft probabilities
        
        Returns:
            (N,) hard assignment indices
        """
        return torch.argmax(soft_assignments, dim=1)


def optimize_clustering(assembly_clusters: List[AssemblyPointCluster],
                       initial_zones: List[BusZone],
                       n_epochs: int = 100,
                       learning_rate: float = 0.01,
                       verbose: bool = True) -> List[BusZone]:
    """
    Optimize zone clustering using PyTorch gradient descent.
    
    Args:
        assembly_clusters: List of assembly point clusters
        initial_zones: Initial zone assignments
        n_epochs: Number of optimization epochs
        learning_rate: Learning rate for Adam optimizer
        verbose: Print progress
    
    Returns:
        Optimized list of BusZone objects
    """
    if not assembly_clusters or not initial_zones:
        return initial_zones
    
    # Extract features
    features = []
    for cluster in assembly_clusters:
        home_cent = cluster.home_centroid
        school_cent = cluster.school_centroid
        student_count = cluster.student_count
        school_diversity = len(cluster.unique_schools)
        
        features.append([
            home_cent[0], home_cent[1],
            school_cent[0], school_cent[1],
            student_count,
            school_diversity
        ])
    
    features_tensor = torch.tensor(features, dtype=torch.float32)
    weights_tensor = torch.tensor([c.student_count for c in assembly_clusters], dtype=torch.float32)
    
    # Initialize model
    n_zones = len(initial_zones)
    bus_capacity = initial_zones[0].capacity if initial_zones else 20
    
    model = SoftClusteringOptimizer(
        n_zones=n_zones,
        feature_dim=features_tensor.shape[1],
        bus_capacity=bus_capacity
    )
    
    # Initialize centroids from initial zones
    with torch.no_grad():
        for i, zone in enumerate(initial_zones):
            zone_features = []
            for cluster in zone.assembly_clusters:
                cluster_idx = assembly_clusters.index(cluster)
                zone_features.append(features_tensor[cluster_idx])
            if zone_features:
                model.zone_centroids[i] = torch.stack(zone_features).mean(dim=0)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    if verbose:
        print(f"\nOptimizing clustering with PyTorch ({n_epochs} epochs)...")
    
    best_loss = float('inf')
    best_assignments = None
    
    for epoch in range(n_epochs):
        optimizer.zero_grad()
        
        soft_assignments, loss_dict = model(features_tensor, weights_tensor)
        loss = loss_dict['total_loss']
        
        loss.backward()
        optimizer.step()
        
        # Track best solution
        if loss.item() < best_loss:
            best_loss = loss.item()
            best_assignments = model.get_hard_assignments(soft_assignments).detach()
        
        if verbose and (epoch % 20 == 0 or epoch == n_epochs - 1):
            print(f"  Epoch {epoch:3d}: loss={loss.item():.2f}, "
                  f"distance={loss_dict['distance_loss']:.2f}, "
                  f"capacity_violation={loss_dict['capacity_loss']:.2f}")
    
    # Convert best assignments to BusZone objects
    optimized_zones = {}
    for cluster, zone_id in zip(assembly_clusters, best_assignments):
        zone_id = zone_id.item()
        if zone_id not in optimized_zones:
            optimized_zones[zone_id] = BusZone(
                zone_id=zone_id,
                assembly_clusters=[],
                capacity=bus_capacity
            )
        optimized_zones[zone_id].assembly_clusters.append(cluster)
    
    zones = [optimized_zones[k] for k in sorted(optimized_zones.keys())]
    
    if verbose:
        print(f"  Optimization complete! Final loss: {best_loss:.2f}")
    
    return zones
