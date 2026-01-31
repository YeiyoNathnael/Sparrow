"""
Simple API example for integrating the clustering system.
"""
import json
from typing import Dict, List
from src.clustering_pipeline import BusPoolingClusteringPipeline
from src.utils.data_structures import Student, AssemblyPoint


class BusClusteringAPI:
    """
    Simple API wrapper for the clustering system.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize API with configuration.
        
        Args:
            config: Dictionary with pipeline configuration
        """
        self.config = config or {
            'bus_capacity': 20,
            'max_schools_per_zone': 3,
            'home_weight': 0.6,
            'school_weight': 0.4,
            'max_walking_distance': 2.0,
            'use_pytorch_optimization': True,
            'optimization_epochs': 100
        }
        
        self.pipeline = BusPoolingClusteringPipeline(**self.config)
    
    def cluster_students(self, 
                        students_data: List[Dict],
                        assembly_points_data: List[Dict],
                        n_zones: int = None) -> Dict:
        """
        Cluster students into bus zones.
        
        Args:
            students_data: List of student dictionaries
            assembly_points_data: List of assembly point dictionaries
            n_zones: Optional number of zones
        
        Returns:
            Dictionary with clustering results
        """
        # Parse input
        students = self._parse_students(students_data)
        assembly_points = self._parse_assembly_points(assembly_points_data)
        
        # Run clustering
        output = self.pipeline.run(
            students=students,
            assembly_points=assembly_points,
            n_zones=n_zones,
            verbose=False
        )
        
        # Return as dictionary
        return output.to_dict()
    
    def get_route_optimizer_input(self,
                                  students_data: List[Dict],
                                  assembly_points_data: List[Dict],
                                  n_zones: int = None) -> Dict:
        """
        Get input format for route optimizer.
        
        Args:
            students_data: List of student dictionaries
            assembly_points_data: List of assembly point dictionaries
            n_zones: Optional number of zones
        
        Returns:
            Route optimizer input dictionary
        """
        students = self._parse_students(students_data)
        assembly_points = self._parse_assembly_points(assembly_points_data)
        
        output = self.pipeline.run(
            students=students,
            assembly_points=assembly_points,
            n_zones=n_zones,
            verbose=False
        )
        
        return self.pipeline.output_formatter.create_route_optimizer_input(output)
    
    def _parse_students(self, students_data: List[Dict]) -> List[Student]:
        """Parse student data from dictionaries."""
        students = []
        for s in students_data:
            students.append(Student(
                student_id=s['student_id'],
                home_location=tuple(s['home_location']),
                school_id=s['school_id'],
                school_location=tuple(s['school_location'])
            ))
        return students
    
    def _parse_assembly_points(self, assembly_data: List[Dict]) -> List[AssemblyPoint]:
        """Parse assembly point data from dictionaries."""
        assembly_points = []
        for a in assembly_data:
            assembly_points.append(AssemblyPoint(
                assembly_id=a['assembly_id'],
                location=tuple(a['location'])
            ))
        return assembly_points


# Example usage
if __name__ == "__main__":
    # Initialize API
    api = BusClusteringAPI(config={
        'bus_capacity': 20,
        'max_schools_per_zone': 3,
        'home_weight': 0.6,
        'school_weight': 0.4
    })
    
    # Example input data
    students_data = [
        {
            'student_id': 's001',
            'home_location': [40.7128, -74.0060],
            'school_id': 'school_A',
            'school_location': [40.7589, -73.9851]
        },
        {
            'student_id': 's002',
            'home_location': [40.7135, -74.0065],
            'school_id': 'school_A',
            'school_location': [40.7589, -73.9851]
        },
        {
            'student_id': 's003',
            'home_location': [40.7140, -74.0070],
            'school_id': 'school_B',
            'school_location': [40.7610, -73.9840]
        },
    ]
    
    assembly_points_data = [
        {
            'assembly_id': 'a001',
            'location': [40.7130, -74.0062]
        },
        {
            'assembly_id': 'a002',
            'location': [40.7138, -74.0068]
        },
    ]
    
    # Get clustering results
    result = api.cluster_students(students_data, assembly_points_data)
    
    print("Clustering Results:")
    print(json.dumps(result, indent=2))
    
    # Get route optimizer input
    route_input = api.get_route_optimizer_input(students_data, assembly_points_data)
    
    print("\nRoute Optimizer Input:")
    print(json.dumps(route_input, indent=2))
