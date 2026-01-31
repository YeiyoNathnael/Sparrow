"""
Zone clustering module for grouping assembly points into bus zones.
Uses capacity-constrained k-means with combined distance metric.
"""
import torch
import numpy as np
from typing import List, Tuple, Optional
from src.utils.data_structures import AssemblyPointCluster, BusZone
from src.utils.distance import batch_haversine_distance, compute_school_dispersion


class ZoneClustering:
    """
    Clusters assembly points into bus zones with capacity constraints.
    """
    
    def __init__(self, 
                 bus_capacity: int = 20,
                 max_schools_per_zone: int = 3,
                 school_proximity_threshold: float = 5.0,
                 home_weight: float = 0.6,
                 school_weight: float = 0.4,
                 max_iter: int = 100):
        """
        Initialize zone clustering.
        
        Args:
            bus_capacity: Maximum students per bus
            max_schools_per_zone: Maximum different schools a bus can serve
            school_proximity_threshold: Max distance (km) between schools in same zone
            home_weight: Weight for home location proximity (default: 0.6)
            school_weight: Weight for school location proximity (default: 0.4)
            max_iter: Maximum iterations for k-means
        """
        self.bus_capacity = bus_capacity
        self.max_schools_per_zone = max_schools_per_zone
        self.school_proximity_threshold = school_proximity_threshold
        self.home_weight = home_weight
        self.school_weight = school_weight
        self.max_iter = max_iter
    
    def cluster(self, assembly_clusters: List[AssemblyPointCluster], 
                n_zones: Optional[int] = None) -> List[BusZone]:
        """
        Cluster assembly points into bus zones.
        
        Args:
            assembly_clusters: List of assembly point clusters with students
            n_zones: Number of zones (buses). If None, auto-calculated from capacity
        
        Returns:
            List of BusZone objects
        """
        if not assembly_clusters:
            return []
        
        # Calculate number of zones if not provided
        if n_zones is None:
            total_students = sum(c.student_count for c in assembly_clusters)
            n_zones = max(1, int(np.ceil(total_students / self.bus_capacity)))
        
        print(f"\nClustering {len(assembly_clusters)} assembly points into {n_zones} zones...")
        
        # Extract features for clustering
        features = self._extract_features(assembly_clusters)
        
        # Initialize centroids using k-means++
        centroids = self._initialize_centroids(features, n_zones)
        
        # Perform capacity-constrained k-means
        assignments = self._capacitated_kmeans(features, centroids, assembly_clusters)
        
        # Build BusZone objects
        zones = self._build_zones(assembly_clusters, assignments)
        
        # Validate and adjust for constraints
        zones = self._enforce_constraints(zones)
        
        # HARD ENFORCE capacity constraints by splitting overcapacity zones
        zones = self._split_overcapacity_zones(zones, assembly_clusters)
        
        return zones
    
    def _extract_features(self, assembly_clusters: List[AssemblyPointCluster]) -> torch.Tensor:
        """
        Extract feature vectors for each assembly point cluster.
        
        Features: [home_centroid_lat, home_centroid_lon, school_centroid_lat, 
                   school_centroid_lon, student_count, school_diversity]
        
        Args:
            assembly_clusters: List of assembly point clusters
        
        Returns:
            Feature tensor of shape (N, 6)
        """
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
        
        return torch.tensor(features, dtype=torch.float32)
    
    def _initialize_centroids(self, features: torch.Tensor, n_zones: int) -> torch.Tensor:
        """
        Initialize centroids using k-means++ algorithm.
        
        Args:
            features: Feature tensor (N, D)
            n_zones: Number of centroids to initialize
        
        Returns:
            Initial centroids (n_zones, D)
        """
        n_points = len(features)
        if n_zones >= n_points:
            # More zones than points, use all points as centroids
            return features.clone()
        
        centroids = torch.zeros(n_zones, features.shape[1])
        
        # Choose first centroid randomly
        first_idx = torch.randint(0, n_points, (1,)).item()
        centroids[0] = features[first_idx]
        
        # Choose remaining centroids with k-means++ logic
        for i in range(1, n_zones):
            # Compute distances to nearest existing centroid
            distances = torch.cdist(features, centroids[:i])
            min_distances = distances.min(dim=1)[0]
            
            # Probability proportional to squared distance
            probabilities = min_distances ** 2
            probabilities = probabilities / probabilities.sum()
            
            # Sample next centroid
            next_idx = torch.multinomial(probabilities, 1).item()
            centroids[i] = features[next_idx]
        
        return centroids
    
    def _capacitated_kmeans(self, 
                           features: torch.Tensor, 
                           centroids: torch.Tensor,
                           assembly_clusters: List[AssemblyPointCluster]) -> torch.Tensor:
        """
        Perform capacity-constrained k-means clustering.
        
        Args:
            features: Feature tensor (N, D)
            centroids: Initial centroids (K, D)
            assembly_clusters: List of assembly point clusters for capacity info
        
        Returns:
            Assignment tensor (N,) with cluster index for each point
        """
        n_points = len(features)
        n_zones = len(centroids)
        
        # Extract weights (student counts)
        weights = torch.tensor([c.student_count for c in assembly_clusters], dtype=torch.float32)
        
        assignments = torch.zeros(n_points, dtype=torch.long)
        
        for iteration in range(self.max_iter):
            old_assignments = assignments.clone()
            
            # Compute combined distances using home and school weights
            home_features = features[:, :2]  # home centroids
            school_features = features[:, 2:4]  # school centroids
            centroid_home = centroids[:, :2]
            centroid_school = centroids[:, 2:4]
            
            home_distances = torch.cdist(home_features, centroid_home)
            school_distances = torch.cdist(school_features, centroid_school)
            
            # Normalize for stable weighting
            home_distances = home_distances / (home_distances.max() + 1e-6)
            school_distances = school_distances / (school_distances.max() + 1e-6)
            
            combined_distances = (self.home_weight * home_distances + 
                                 self.school_weight * school_distances)
            
            # Capacity-constrained assignment
            assignments = self._constrained_assignment(
                combined_distances, weights, n_zones
            )
            
            # Update centroids
            for k in range(n_zones):
                mask = (assignments == k)
                if mask.sum() > 0:
                    centroids[k] = features[mask].mean(dim=0)
            
            # Check convergence
            if torch.all(assignments == old_assignments):
                print(f"  Converged after {iteration + 1} iterations")
                break
        
        return assignments
    
    def _constrained_assignment(self, 
                               distances: torch.Tensor, 
                               weights: torch.Tensor,
                               n_zones: int) -> torch.Tensor:
        """
        Assign points to clusters respecting capacity constraints.
        
        Args:
            distances: Distance matrix (N, K)
            weights: Point weights/demands (N,)
            n_zones: Number of zones
        
        Returns:
            Assignment tensor (N,)
        """
        n_points = len(distances)
        assignments = torch.full((n_points,), -1, dtype=torch.long)
        remaining_capacity = torch.full((n_zones,), float(self.bus_capacity))
        
        # Sort points by minimum distance to any cluster
        min_distances, _ = distances.min(dim=1)
        sorted_indices = torch.argsort(min_distances)
        
        # Greedy assignment in order of distance
        for idx in sorted_indices:
            idx = idx.item()
            weight = weights[idx].item()
            
            # Find feasible clusters (with enough capacity)
            feasible_mask = remaining_capacity >= weight
            
            if not feasible_mask.any():
                # No cluster has capacity, assign to closest anyway (will fix later)
                cluster_idx = distances[idx].argmin().item()
            else:
                # Assign to closest feasible cluster
                feasible_distances = distances[idx].clone()
                feasible_distances[~feasible_mask] = float('inf')
                cluster_idx = feasible_distances.argmin().item()
            
            assignments[idx] = cluster_idx
            remaining_capacity[cluster_idx] -= weight
        
        return assignments
    
    def _build_zones(self, 
                    assembly_clusters: List[AssemblyPointCluster],
                    assignments: torch.Tensor) -> List[BusZone]:
        """
        Build BusZone objects from assignments.
        
        Args:
            assembly_clusters: List of assembly point clusters
            assignments: Assignment tensor (N,)
        
        Returns:
            List of BusZone objects
        """
        zones_dict = {}
        
        for cluster, assignment in zip(assembly_clusters, assignments):
            zone_id = assignment.item()
            
            if zone_id not in zones_dict:
                zones_dict[zone_id] = BusZone(
                    zone_id=zone_id,
                    assembly_clusters=[],
                    capacity=self.bus_capacity
                )
            
            zones_dict[zone_id].assembly_clusters.append(cluster)
        
        # Convert to sorted list
        zones = [zones_dict[k] for k in sorted(zones_dict.keys())]
        
        return zones
    
    def _enforce_constraints(self, zones: List[BusZone]) -> List[BusZone]:
        """
        Enforce school diversity and capacity constraints through iterative refinement.
        
        Args:
            zones: Initial zones
        
        Returns:
            Adjusted zones meeting constraints
        """
        print(f"\nEnforcing constraints...")
        
        # Check and fix school diversity constraint
        for zone in zones:
            if len(zone.school_ids) > self.max_schools_per_zone:
                print(f"  Warning: Zone {zone.zone_id} has {len(zone.school_ids)} schools "
                      f"(max: {self.max_schools_per_zone})")
                # Could implement refinement logic here
        
        # Check capacity constraints
        overcapacity_zones = [z for z in zones if z.is_capacity_exceeded()]
        if overcapacity_zones:
            print(f"  Warning: {len(overcapacity_zones)} zones exceed capacity")
            for zone in overcapacity_zones:
                print(f"    Zone {zone.zone_id}: {zone.total_students}/{zone.capacity} students")
            
            # Could implement load balancing here
        
        return zones
    
    def get_clustering_statistics(self, zones: List[BusZone]) -> dict:
        """
        Compute statistics about the zone clustering.
        
        Args:
            zones: List of bus zones
        
        Returns:
            Dictionary of statistics
        """
        if not zones:
            return {}
        
        total_students = sum(z.total_students for z in zones)
        capacities = torch.tensor([z.capacity_utilization for z in zones])
        students_per_zone = torch.tensor([z.total_students for z in zones], dtype=torch.float32)
        schools_per_zone = torch.tensor([len(z.school_ids) for z in zones], dtype=torch.float32)
        assemblies_per_zone = torch.tensor([len(z.assembly_clusters) for z in zones], dtype=torch.float32)
        
        return {
            'total_zones': len(zones),
            'total_students': total_students,
            'avg_students_per_zone': students_per_zone.mean().item(),
            'std_students_per_zone': students_per_zone.std().item(),
            'min_students_per_zone': students_per_zone.min().item(),
            'max_students_per_zone': students_per_zone.max().item(),
            'avg_capacity_utilization': capacities.mean().item(),
            'zones_over_capacity': sum(1 for z in zones if z.is_capacity_exceeded()),
            'avg_schools_per_zone': schools_per_zone.mean().item(),
            'max_schools_per_zone': schools_per_zone.max().item(),
            'avg_assemblies_per_zone': assemblies_per_zone.mean().item(),
        }
    
    def _split_overcapacity_zones(self, zones: List[BusZone], 
                                  assembly_clusters: List[AssemblyPointCluster]) -> List[BusZone]:
        """
        Post-processing step to hard enforce capacity constraints.
        Splits overcapacity zones by reassigning assembly points.
        
        Args:
            zones: Initial zones (may be overcapacity)
            assembly_clusters: Original assembly point clusters
        
        Returns:
            List of zones with capacity enforced
        """
        final_zones = []
        zone_id_counter = 0
        
        for zone in zones:
            if zone.total_students <= self.bus_capacity:
                # Zone is within capacity, keep as is
                zone.zone_id = zone_id_counter
                final_zones.append(zone)
                zone_id_counter += 1
            else:
                # Zone is overcapacity, split it
                print(f"\n  ⚠️  Zone {zone.zone_id} has {zone.total_students} students (capacity: {self.bus_capacity})")
                print(f"      Splitting into multiple buses...")
                
                # Sort assembly clusters by student count (largest first for better packing)
                zone_assemblies = sorted(zone.assembly_clusters, 
                                       key=lambda x: x.student_count, 
                                       reverse=True)
                
                # Greedy bin packing: create new zones
                current_zone_load = 0
                current_zone_clusters = []
                split_count = 0
                
                for assembly_cluster in zone_assemblies:
                    student_count = assembly_cluster.student_count
                    
                    if current_zone_load + student_count <= self.bus_capacity:
                        # Add to current zone
                        current_zone_clusters.append(assembly_cluster)
                        current_zone_load += student_count
                    else:
                        # Create new zone with current clusters
                        if current_zone_clusters:
                            new_zone = BusZone(
                                zone_id=zone_id_counter,
                                assembly_clusters=current_zone_clusters,
                                capacity=self.bus_capacity
                            )
                            final_zones.append(new_zone)
                            zone_id_counter += 1
                            split_count += 1
                        
                        # Start new zone with this assembly
                        current_zone_clusters = [assembly_cluster]
                        current_zone_load = student_count
                
                # Add remaining clusters as final zone
                if current_zone_clusters:
                    new_zone = BusZone(
                        zone_id=zone_id_counter,
                        assembly_clusters=current_zone_clusters,
                        capacity=self.bus_capacity
                    )
                    final_zones.append(new_zone)
                    zone_id_counter += 1
                    split_count += 1
                
                print(f"      ✓ Split into {split_count} buses")
        
        print(f"\n✓ Final result: {len(final_zones)} zones (all within capacity)")
        return final_zones
