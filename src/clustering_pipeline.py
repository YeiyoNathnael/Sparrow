"""
Main clustering pipeline orchestrating all components.
Entry point for bus pooling clustering system.
"""
from typing import List, Optional, Dict
from src.utils.data_structures import (
    Student, AssemblyPoint, ClusteringInput, ClusteringOutput
)
from src.models.student_assignment import StudentAssignment
from src.models.zone_clustering import ZoneClustering
from src.models.pytorch_optimizer import optimize_clustering
from src.models.output import OutputFormatter
from src.utils.metrics import ClusteringMetrics


class BusPoolingClusteringPipeline:
    """
    End-to-end pipeline for clustering students into bus zones.
    """
    
    def __init__(self, 
                 bus_capacity: int = 20,
                 max_schools_per_zone: int = 3,
                 school_proximity_threshold: float = 5.0,
                 home_weight: float = 0.6,
                 school_weight: float = 0.4,
                 max_walking_distance: float = 2.0,
                 use_pytorch_optimization: bool = True,
                 optimization_epochs: int = 100):
        """
        Initialize clustering pipeline.
        
        Args:
            bus_capacity: Maximum students per bus (default: 20)
            max_schools_per_zone: Max different schools per bus (default: 3)
            school_proximity_threshold: Max km between schools in zone (default: 5.0)
            home_weight: Weight for home proximity (default: 0.6)
            school_weight: Weight for school proximity (default: 0.4)
            max_walking_distance: Max walking distance to assembly point (default: 2.0 km)
            use_pytorch_optimization: Enable PyTorch gradient-based refinement (default: True)
            optimization_epochs: Number of optimization epochs (default: 100)
        """
        self.bus_capacity = bus_capacity
        self.max_schools_per_zone = max_schools_per_zone
        self.school_proximity_threshold = school_proximity_threshold
        self.home_weight = home_weight
        self.school_weight = school_weight
        self.max_walking_distance = max_walking_distance
        self.use_pytorch_optimization = use_pytorch_optimization
        self.optimization_epochs = optimization_epochs
        
        # Initialize components
        self.student_assigner = None
        self.zone_clusterer = None
        self.metrics_computer = ClusteringMetrics()
        self.output_formatter = OutputFormatter()
    
    def run(self, 
            students: List[Student],
            assembly_points: List[AssemblyPoint],
            n_zones: Optional[int] = None,
            verbose: bool = True) -> ClusteringOutput:
        """
        Run the complete clustering pipeline.
        
        Args:
            students: List of students with home and school locations
            assembly_points: List of predefined assembly points
            n_zones: Number of zones (buses). If None, auto-calculated from capacity
            verbose: Print progress and statistics (default: True)
        
        Returns:
            ClusteringOutput with zones and metrics
        """
        if verbose:
            print("\n" + "="*80)
            print("BUS POOLING CLUSTERING PIPELINE")
            print("="*80)
            print(f"\nInput:")
            print(f"  Students: {len(students)}")
            print(f"  Assembly Points: {len(assembly_points)}")
            print(f"  Bus Capacity: {self.bus_capacity}")
            print(f"  Max Schools per Zone: {self.max_schools_per_zone}")
            print(f"  Distance Weights: home={self.home_weight}, school={self.school_weight}")
        
        # Stage 1: Assign students to assembly points
        if verbose:
            print("\n" + "-"*80)
            print("STAGE 1: Student → Assembly Point Assignment")
            print("-"*80)
        
        self.student_assigner = StudentAssignment(
            assembly_points=assembly_points,
            max_walking_distance=self.max_walking_distance
        )
        
        assembly_clusters = self.student_assigner.assign_students(students)
        
        if verbose:
            assignment_stats = self.student_assigner.get_assignment_statistics(assembly_clusters)
            print(f"\nAssignment complete:")
            print(f"  Assembly points used: {assignment_stats['total_assembly_points_used']}")
            print(f"  Avg walking distance: {assignment_stats['avg_walking_distance_km']:.3f} km")
            print(f"  Max walking distance: {assignment_stats['max_walking_distance_km']:.3f} km")
        
        # Stage 2: Cluster assembly points into bus zones
        if verbose:
            print("\n" + "-"*80)
            print("STAGE 2: Assembly Point → Bus Zone Clustering")
            print("-"*80)
        
        self.zone_clusterer = ZoneClustering(
            bus_capacity=self.bus_capacity,
            max_schools_per_zone=self.max_schools_per_zone,
            school_proximity_threshold=self.school_proximity_threshold,
            home_weight=self.home_weight,
            school_weight=self.school_weight
        )
        
        zones = self.zone_clusterer.cluster(assembly_clusters, n_zones=n_zones)
        
        if verbose:
            clustering_stats = self.zone_clusterer.get_clustering_statistics(zones)
            print(f"\nInitial clustering complete:")
            print(f"  Zones created: {clustering_stats['total_zones']}")
            print(f"  Avg students per zone: {clustering_stats['avg_students_per_zone']:.1f}")
            print(f"  Avg capacity utilization: {clustering_stats['avg_capacity_utilization']:.1%}")
        
        # Stage 3: PyTorch optimization (optional)
        if self.use_pytorch_optimization:
            if verbose:
                print("\n" + "-"*80)
                print("STAGE 3: PyTorch Gradient-Based Optimization")
                print("-"*80)
            
            zones = optimize_clustering(
                assembly_clusters=assembly_clusters,
                initial_zones=zones,
                n_epochs=self.optimization_epochs,
                verbose=verbose
            )
        
        # Compute final metrics
        if verbose:
            print("\n" + "-"*80)
            print("COMPUTING QUALITY METRICS")
            print("-"*80)
        
        metrics = self.metrics_computer.compute_all_metrics(zones, assembly_clusters)
        
        if verbose:
            self.metrics_computer.print_metrics_report(metrics)
        
        # Create output
        output = self.output_formatter.format_zones(zones, metrics)
        
        if verbose:
            self.output_formatter.print_summary(output)
        
        return output
    
    def run_from_dict(self, 
                     input_data: Dict,
                     verbose: bool = True) -> ClusteringOutput:
        """
        Run pipeline from dictionary input.
        
        Args:
            input_data: Dictionary with keys:
                - 'students': List of dicts with student_id, home_location, school_id, school_location
                - 'assembly_points': List of dicts with assembly_id, location
                - 'n_zones': Optional number of zones
            verbose: Print progress
        
        Returns:
            ClusteringOutput
        """
        # Parse students
        students = []
        for s in input_data['students']:
            students.append(Student(
                student_id=s['student_id'],
                home_location=tuple(s['home_location']),
                school_id=s['school_id'],
                school_location=tuple(s['school_location'])
            ))
        
        # Parse assembly points
        assembly_points = []
        for a in input_data['assembly_points']:
            assembly_points.append(AssemblyPoint(
                assembly_id=a['assembly_id'],
                location=tuple(a['location'])
            ))
        
        n_zones = input_data.get('n_zones', None)
        
        return self.run(students, assembly_points, n_zones, verbose)


def main():
    """
    Example usage of the clustering pipeline.
    """
    import numpy as np
    
    # Generate synthetic data for demonstration
    np.random.seed(42)
    
    # Create students with home locations clustered in residential areas
    # and school locations representing different schools
    n_students = 100
    n_assembly_points = 15
    n_schools = 5
    
    # Generate school locations
    school_locations = [
        (40.7128 + np.random.randn() * 0.02, -74.0060 + np.random.randn() * 0.02)
        for _ in range(n_schools)
    ]
    
    # Generate students
    students = []
    for i in range(n_students):
        # Cluster students in residential areas
        cluster_id = i % 5
        home_lat = 40.7128 + (cluster_id * 0.03) + np.random.randn() * 0.01
        home_lon = -74.0060 + (cluster_id * 0.03) + np.random.randn() * 0.01
        
        # Randomly assign to schools
        school_id = f"school_{i % n_schools}"
        school_location = school_locations[i % n_schools]
        
        students.append(Student(
            student_id=f"student_{i:03d}",
            home_location=(home_lat, home_lon),
            school_id=school_id,
            school_location=school_location
        ))
    
    # Generate assembly points near residential clusters
    assembly_points = []
    for i in range(n_assembly_points):
        cluster_id = i % 5
        lat = 40.7128 + (cluster_id * 0.03) + np.random.randn() * 0.005
        lon = -74.0060 + (cluster_id * 0.03) + np.random.randn() * 0.005
        
        assembly_points.append(AssemblyPoint(
            assembly_id=f"assembly_{i:02d}",
            location=(lat, lon)
        ))
    
    # Run pipeline
    pipeline = BusPoolingClusteringPipeline(
        bus_capacity=20,
        max_schools_per_zone=3,
        use_pytorch_optimization=True,
        optimization_epochs=50
    )
    
    output = pipeline.run(
        students=students,
        assembly_points=assembly_points,
        verbose=True
    )
    
    # Save output
    pipeline.output_formatter.to_json(output, filepath='clustering_output.json')
    
    # Create route optimizer input
    route_input = pipeline.output_formatter.create_route_optimizer_input(output)
    print("\nRoute optimizer input prepared with", len(route_input['routes']), "routes")


if __name__ == "__main__":
    main()
