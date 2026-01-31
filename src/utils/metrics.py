"""
Clustering quality metrics for evaluation.
"""
import torch
import numpy as np
from typing import List, Dict
from src.utils.data_structures import BusZone, AssemblyPointCluster
from src.utils.distance import batch_haversine_distance, compute_centroid


class ClusteringMetrics:
    """
    Compute quality metrics for clustering evaluation.
    """
    
    @staticmethod
    def compute_all_metrics(zones: List[BusZone],
                           assembly_clusters: List[AssemblyPointCluster]) -> Dict[str, float]:
        """
        Compute comprehensive clustering quality metrics.
        
        Args:
            zones: List of bus zones
            assembly_clusters: List of all assembly point clusters
        
        Returns:
            Dictionary of metric values
        """
        metrics = {}
        
        # Basic statistics
        metrics.update(ClusteringMetrics._basic_statistics(zones))
        
        # Distance-based metrics
        metrics.update(ClusteringMetrics._distance_metrics(zones, assembly_clusters))
        
        # Cluster quality metrics
        metrics.update(ClusteringMetrics._cluster_quality_metrics(zones))
        
        # Capacity and balance metrics
        metrics.update(ClusteringMetrics._capacity_metrics(zones))
        
        # School distribution metrics
        metrics.update(ClusteringMetrics._school_distribution_metrics(zones))
        
        return metrics
    
    @staticmethod
    def _basic_statistics(zones: List[BusZone]) -> Dict[str, float]:
        """Basic statistical metrics."""
        if not zones:
            return {}
        
        students_per_zone = [z.total_students for z in zones]
        
        return {
            'total_zones': len(zones),
            'total_students': sum(students_per_zone),
            'avg_students_per_zone': np.mean(students_per_zone),
            'std_students_per_zone': np.std(students_per_zone),
            'min_students_per_zone': min(students_per_zone),
            'max_students_per_zone': max(students_per_zone)
        }
    
    @staticmethod
    def _distance_metrics(zones: List[BusZone], 
                         assembly_clusters: List[AssemblyPointCluster]) -> Dict[str, float]:
        """
        Compute distance-based metrics.
        """
        total_walking_distance = 0.0
        walking_distances = []
        
        # Calculate all walking distances
        for cluster in assembly_clusters:
            distances = cluster.get_walking_distances()
            walking_distances.extend(distances)
            total_walking_distance += sum(distances)
        
        # Calculate zone compactness (average distance to zone centroid)
        zone_compactness = []
        for zone in zones:
            if not zone.assembly_clusters:
                continue
            
            zone_cent = torch.tensor(zone.zone_centroid).unsqueeze(0)
            assembly_locs = torch.tensor([c.assembly_point.location 
                                         for c in zone.assembly_clusters])
            
            if len(assembly_locs) > 0:
                distances = batch_haversine_distance(assembly_locs, zone_cent)
                zone_compactness.append(distances.mean().item())
        
        return {
            'avg_walking_distance_km': np.mean(walking_distances) if walking_distances else 0.0,
            'max_walking_distance_km': max(walking_distances) if walking_distances else 0.0,
            'total_walking_distance_km': total_walking_distance,
            'std_walking_distance_km': np.std(walking_distances) if walking_distances else 0.0,
            'avg_zone_compactness_km': np.mean(zone_compactness) if zone_compactness else 0.0
        }
    
    @staticmethod
    def _cluster_quality_metrics(zones: List[BusZone]) -> Dict[str, float]:
        """
        Compute clustering quality metrics (silhouette, cohesion, separation).
        """
        if len(zones) < 2:
            return {
                'silhouette_score': 0.0,
                'avg_intra_cluster_distance': 0.0,
                'avg_inter_cluster_distance': 0.0
            }
        
        # Collect all assembly point locations and their zone assignments
        all_locations = []
        all_assignments = []
        
        for zone_idx, zone in enumerate(zones):
            for cluster in zone.assembly_clusters:
                all_locations.append(cluster.assembly_point.location)
                all_assignments.append(zone_idx)
        
        if len(all_locations) < 2:
            return {
                'silhouette_score': 0.0,
                'avg_intra_cluster_distance': 0.0,
                'avg_inter_cluster_distance': 0.0
            }
        
        locations_tensor = torch.tensor(all_locations, dtype=torch.float32)
        assignments_tensor = torch.tensor(all_assignments)
        
        # Compute distance matrix
        distance_matrix = batch_haversine_distance(locations_tensor, locations_tensor)
        
        # Compute silhouette score
        silhouette_scores = []
        intra_distances = []
        inter_distances = []
        
        for i in range(len(all_locations)):
            same_cluster = (assignments_tensor == assignments_tensor[i])
            diff_cluster = ~same_cluster
            
            # Intra-cluster distance (a)
            if same_cluster.sum() > 1:
                a = distance_matrix[i][same_cluster].sum() / (same_cluster.sum() - 1)
                intra_distances.append(a.item())
            else:
                a = 0.0
            
            # Inter-cluster distance (b) - minimum average distance to other clusters
            b = float('inf')
            for zone_idx in range(len(zones)):
                if zone_idx != assignments_tensor[i]:
                    other_cluster = (assignments_tensor == zone_idx)
                    if other_cluster.sum() > 0:
                        avg_dist = distance_matrix[i][other_cluster].mean()
                        b = min(b, avg_dist.item())
            
            if b != float('inf'):
                inter_distances.append(b)
                # Silhouette coefficient
                s = (b - a) / max(a, b) if max(a, b) > 0 else 0
                silhouette_scores.append(s)
        
        return {
            'silhouette_score': np.mean(silhouette_scores) if silhouette_scores else 0.0,
            'avg_intra_cluster_distance': np.mean(intra_distances) if intra_distances else 0.0,
            'avg_inter_cluster_distance': np.mean(inter_distances) if inter_distances else 0.0
        }
    
    @staticmethod
    def _capacity_metrics(zones: List[BusZone]) -> Dict[str, float]:
        """
        Compute capacity utilization and balance metrics.
        """
        if not zones:
            return {}
        
        utilizations = [z.capacity_utilization for z in zones]
        over_capacity = [z for z in zones if z.is_capacity_exceeded()]
        
        # Load balance (coefficient of variation)
        loads = [z.total_students for z in zones]
        cv = np.std(loads) / np.mean(loads) if np.mean(loads) > 0 else 0
        
        return {
            'avg_capacity_utilization': np.mean(utilizations),
            'min_capacity_utilization': min(utilizations),
            'max_capacity_utilization': max(utilizations),
            'std_capacity_utilization': np.std(utilizations),
            'zones_over_capacity': len(over_capacity),
            'pct_zones_over_capacity': len(over_capacity) / len(zones) * 100,
            'load_balance_cv': cv,  # Lower is more balanced
            'total_capacity_wasted': sum(max(0, z.capacity - z.total_students) for z in zones)
        }
    
    @staticmethod
    def _school_distribution_metrics(zones: List[BusZone]) -> Dict[str, float]:
        """
        Compute metrics related to school distribution across zones.
        """
        if not zones:
            return {}
        
        schools_per_zone = [len(z.school_ids) for z in zones]
        
        # Calculate school diversity penalty
        school_diversity_penalties = []
        for zone in zones:
            if len(zone.school_ids) > 1:
                # Get all school locations in this zone
                school_locs = []
                for cluster in zone.assembly_clusters:
                    for student in cluster.students:
                        school_locs.append(student.school_location)
                
                if len(school_locs) > 1:
                    school_locs_tensor = torch.tensor(list(set(school_locs)), dtype=torch.float32)
                    # Compute variance of school locations
                    variance = school_locs_tensor.var(dim=0).sum().item()
                    school_diversity_penalties.append(variance)
        
        return {
            'avg_schools_per_zone': np.mean(schools_per_zone),
            'max_schools_per_zone': max(schools_per_zone),
            'min_schools_per_zone': min(schools_per_zone),
            'std_schools_per_zone': np.std(schools_per_zone),
            'zones_with_multiple_schools': sum(1 for s in schools_per_zone if s > 1),
            'avg_school_diversity_penalty': np.mean(school_diversity_penalties) if school_diversity_penalties else 0.0
        }
    
    @staticmethod
    def print_metrics_report(metrics: Dict[str, float]) -> None:
        """
        Print formatted metrics report.
        
        Args:
            metrics: Dictionary of metrics from compute_all_metrics
        """
        print("\n" + "="*80)
        print("CLUSTERING QUALITY METRICS")
        print("="*80)
        
        categories = {
            'Basic Statistics': [
                'total_zones', 'total_students', 'avg_students_per_zone',
                'std_students_per_zone', 'min_students_per_zone', 'max_students_per_zone'
            ],
            'Distance Metrics': [
                'avg_walking_distance_km', 'max_walking_distance_km',
                'total_walking_distance_km', 'std_walking_distance_km',
                'avg_zone_compactness_km'
            ],
            'Cluster Quality': [
                'silhouette_score', 'avg_intra_cluster_distance',
                'avg_inter_cluster_distance'
            ],
            'Capacity & Balance': [
                'avg_capacity_utilization', 'min_capacity_utilization',
                'max_capacity_utilization', 'zones_over_capacity',
                'pct_zones_over_capacity', 'load_balance_cv'
            ],
            'School Distribution': [
                'avg_schools_per_zone', 'max_schools_per_zone',
                'zones_with_multiple_schools', 'avg_school_diversity_penalty'
            ]
        }
        
        for category, metric_keys in categories.items():
            print(f"\n{category}:")
            print("-" * 80)
            for key in metric_keys:
                if key in metrics:
                    value = metrics[key]
                    if isinstance(value, float):
                        if 'pct' in key or 'utilization' in key:
                            print(f"  {key:.<50} {value:>10.2f}%")
                        else:
                            print(f"  {key:.<50} {value:>10.3f}")
                    else:
                        print(f"  {key:.<50} {value:>10}")
        
        print("\n" + "="*80 + "\n")
