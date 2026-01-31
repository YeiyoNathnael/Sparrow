"""
Student-to-assembly point assignment module.
Assigns students to nearest assembly points based on home location.
"""
import torch
from typing import List, Dict
from src.utils.data_structures import Student, AssemblyPoint, AssemblyPointCluster
from src.utils.distance import batch_haversine_distance


class StudentAssignment:
    """
    Assigns students to assembly points based on proximity.
    """
    
    def __init__(self, assembly_points: List[AssemblyPoint], max_walking_distance: float = 2.0):
        """
        Initialize student assignment.
        
        Args:
            assembly_points: List of available assembly points
            max_walking_distance: Maximum acceptable walking distance in km (default: 2.0)
        """
        self.assembly_points = assembly_points
        self.max_walking_distance = max_walking_distance
        
    def assign_students(self, students: List[Student]) -> List[AssemblyPointCluster]:
        """
        Assign each student to nearest assembly point.
        
        Args:
            students: List of students to assign
        
        Returns:
            List of AssemblyPointCluster objects
        """
        # Convert to tensors for efficient computation
        student_homes = torch.tensor(
            [s.home_location for s in students],
            dtype=torch.float32
        )
        assembly_locations = torch.tensor(
            [a.location for a in self.assembly_points],
            dtype=torch.float32
        )
        
        # Compute distance matrix: (num_students, num_assemblies)
        distance_matrix = batch_haversine_distance(student_homes, assembly_locations)
        
        # Assign each student to nearest assembly point
        nearest_assembly_indices = torch.argmin(distance_matrix, dim=1)
        walking_distances = torch.gather(distance_matrix, 1, nearest_assembly_indices.unsqueeze(1)).squeeze(1)
        
        # Create assembly point clusters
        clusters_dict: Dict[int, AssemblyPointCluster] = {}
        
        for student_idx, (assembly_idx, walking_dist) in enumerate(zip(nearest_assembly_indices, walking_distances)):
            assembly_idx = assembly_idx.item()
            walking_dist = walking_dist.item()
            
            # Check walking distance constraint
            if walking_dist > self.max_walking_distance:
                print(f"Warning: Student {students[student_idx].student_id} assigned to assembly "
                      f"{self.assembly_points[assembly_idx].assembly_id} with walking distance "
                      f"{walking_dist:.2f} km (exceeds max {self.max_walking_distance} km)")
            
            # Create cluster if it doesn't exist
            if assembly_idx not in clusters_dict:
                clusters_dict[assembly_idx] = AssemblyPointCluster(
                    assembly_point=self.assembly_points[assembly_idx],
                    students=[]
                )
            
            # Add student to cluster
            clusters_dict[assembly_idx].students.append(students[student_idx])
        
        # Convert to list and filter empty clusters
        clusters = [cluster for cluster in clusters_dict.values() if cluster.student_count > 0]
        
        return clusters
    
    def get_assignment_statistics(self, clusters: List[AssemblyPointCluster]) -> Dict[str, float]:
        """
        Compute statistics about student-to-assembly assignments.
        
        Args:
            clusters: List of assembly point clusters
        
        Returns:
            Dictionary of statistics
        """
        total_students = sum(c.student_count for c in clusters)
        
        all_walking_distances = []
        for cluster in clusters:
            all_walking_distances.extend(cluster.get_walking_distances())
        
        walking_distances_tensor = torch.tensor(all_walking_distances)
        
        return {
            'total_students': total_students,
            'total_assembly_points_used': len(clusters),
            'avg_students_per_assembly': total_students / len(clusters) if clusters else 0,
            'avg_walking_distance_km': walking_distances_tensor.mean().item(),
            'max_walking_distance_km': walking_distances_tensor.max().item(),
            'min_walking_distance_km': walking_distances_tensor.min().item(),
            'std_walking_distance_km': walking_distances_tensor.std().item(),
            'students_exceeding_max_walk': sum(1 for d in all_walking_distances if d > self.max_walking_distance)
        }
    
    def visualize_clusters(self, clusters: List[AssemblyPointCluster]) -> None:
        """
        Print summary of assembly point clusters.
        
        Args:
            clusters: List of assembly point clusters
        """
        print("\n" + "="*80)
        print("ASSEMBLY POINT CLUSTERING SUMMARY")
        print("="*80)
        
        for cluster in clusters:
            print(f"\nAssembly Point: {cluster.assembly_point.assembly_id}")
            print(f"  Location: {cluster.assembly_point.location}")
            print(f"  Students: {cluster.student_count}")
            print(f"  Schools served: {len(cluster.unique_schools)} - {cluster.unique_schools}")
            print(f"  School distribution: {cluster.school_distribution}")
            
            walking_dists = cluster.get_walking_distances()
            if walking_dists:
                print(f"  Walking distances: avg={sum(walking_dists)/len(walking_dists):.2f} km, "
                      f"max={max(walking_dists):.2f} km")
        
        stats = self.get_assignment_statistics(clusters)
        print("\n" + "-"*80)
        print("OVERALL STATISTICS")
        print("-"*80)
        for key, value in stats.items():
            print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
        print("="*80 + "\n")
