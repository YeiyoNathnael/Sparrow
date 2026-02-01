"""
Output formatting module for clustering results.
Provides structured output for downstream route optimization.
"""
import json
import numpy as np
from typing import List, Dict, Any
from src.utils.data_structures import BusZone, ClusteringOutput


class OutputFormatter:
    """
    Formats clustering results for downstream consumption.
    """
    
    @staticmethod
    def _convert_to_native_types(obj):
        """
        Recursively convert numpy/torch types to native Python types for JSON serialization.
        """
        if isinstance(obj, dict):
            return {key: OutputFormatter._convert_to_native_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [OutputFormatter._convert_to_native_types(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, 'item'):  # PyTorch tensors
            return obj.item()
        else:
            return obj
    
    @staticmethod
    def format_zones(zones: List[BusZone], metrics: Dict[str, float] = None) -> ClusteringOutput:
        """
        Create structured output from zones.
        
        Args:
            zones: List of bus zones
            metrics: Optional clustering quality metrics
        
        Returns:
            ClusteringOutput object
        """
        if metrics is None:
            metrics = {}
        
        return ClusteringOutput(zones=zones, clustering_metrics=metrics)
    
    @staticmethod
    def to_json(output: ClusteringOutput, filepath: str = None, indent: int = 2) -> str:
        """
        Convert clustering output to JSON.
        
        Args:
            output: ClusteringOutput object
            filepath: Optional path to save JSON file
            indent: JSON indentation (default: 2)
        
        Returns:
            JSON string
        """
        output_dict = output.to_dict()
        # Convert numpy/torch types to native Python types
        output_dict = OutputFormatter._convert_to_native_types(output_dict)
        json_str = json.dumps(output_dict, indent=indent)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
            print(f"\nOutput saved to: {filepath}")
        
        return json_str
    
    @staticmethod
    def print_summary(output: ClusteringOutput) -> None:
        """
        Print human-readable summary of clustering results.
        
        Args:
            output: ClusteringOutput object
        """
        print("\n" + "="*80)
        print("CLUSTERING RESULTS SUMMARY")
        print("="*80)
        
        output_dict = output.to_dict()
        summary = output_dict['summary']
        
        print(f"\nOverall Statistics:")
        print(f"  Total Zones (Buses): {summary['total_zones']}")
        print(f"  Total Students: {summary['total_students']}")
        print(f"  Avg Students per Zone: {summary['avg_students_per_zone']:.1f}")
        print(f"  Avg Capacity Utilization: {summary['avg_capacity_utilization']:.1%}")
        print(f"  Zones Over Capacity: {summary['zones_over_capacity']}")
        
        if output.clustering_metrics:
            print(f"\nClustering Quality Metrics:")
            for key, value in output.clustering_metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")
        
        print("\n" + "-"*80)
        print("ZONE DETAILS")
        print("-"*80)
        
        for zone_data in output_dict['zones']:
            print(f"\nZone {zone_data['zone_id']}:")
            print(f"  Students: {zone_data['student_count']}/{zone_data['capacity']} "
                  f"({zone_data['capacity_utilization']:.1%})")
            print(f"  Assembly Points: {len(zone_data['assembly_nodes'])} - {zone_data['assembly_nodes']}")
            print(f"  Schools Served: {len(zone_data['schools'])} - {zone_data['schools']}")
            print(f"  School Distribution: {zone_data['school_distribution']}")
            print(f"  Zone Centroid: ({zone_data['zone_centroid'][0]:.4f}, {zone_data['zone_centroid'][1]:.4f})")
        
        print("\n" + "="*80 + "\n")
    
    @staticmethod
    def create_route_optimizer_input(output: ClusteringOutput) -> Dict[str, Any]:
        """
        Create input format specifically for route optimization module.
        
        Args:
            output: ClusteringOutput object
        
        Returns:
            Dictionary with format optimized for routing
        """
        routes = []
        
        for zone in output.zones:
            # Get all assembly point locations
            assembly_nodes = []
            for cluster in zone.assembly_clusters:
                assembly_nodes.append({
                    'node_id': cluster.assembly_point.assembly_id,
                    'type': 'pickup',
                    'location': {
                        'lat': cluster.assembly_point.location[0],
                        'lon': cluster.assembly_point.location[1]
                    },
                    'demand': cluster.student_count,
                    'students': [s.student_id for s in cluster.students]
                })
            
            # Get all school locations (dropoff points)
            school_nodes = []
            unique_schools = {}
            for cluster in zone.assembly_clusters:
                for student in cluster.students:
                    if student.school_id not in unique_schools:
                        unique_schools[student.school_id] = {
                            'location': student.school_location,
                            'students': []
                        }
                    unique_schools[student.school_id]['students'].append(student.student_id)
            
            for school_id, school_data in unique_schools.items():
                school_nodes.append({
                    'node_id': school_id,
                    'type': 'dropoff',
                    'location': {
                        'lat': school_data['location'][0],
                        'lon': school_data['location'][1]
                    },
                    'students_to_drop': school_data['students']
                })
            
            routes.append({
                'route_id': zone.zone_id,
                'capacity': zone.capacity,
                'total_students': zone.total_students,
                'buses_needed': zone.buses_needed,  # Number of buses required for this zone
                'pickup_nodes': assembly_nodes,
                'dropoff_nodes': school_nodes,
                'constraints': {
                    'max_capacity': zone.capacity,
                    'current_load': zone.total_students
                }
            })
        
        return {
            'routes': routes,
            'metadata': {
                'total_routes': len(routes),
                'total_students': sum(r['total_students'] for r in routes),
                'clustering_quality': output.clustering_metrics
            }
        }
    
    @staticmethod
    def export_for_visualization(output: ClusteringOutput, filepath: str = None) -> Dict[str, Any]:
        """
        Export data in format suitable for map visualization.
        
        Args:
            output: ClusteringOutput object
            filepath: Optional path to save JSON file
        
        Returns:
            Dictionary with GeoJSON-style format
        """
        features = []
        
        for zone in output.zones:
            # Add assembly points
            for cluster in zone.assembly_clusters:
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [
                            cluster.assembly_point.location[1],  # lon
                            cluster.assembly_point.location[0]   # lat
                        ]
                    },
                    'properties': {
                        'type': 'assembly_point',
                        'id': cluster.assembly_point.assembly_id,
                        'zone_id': zone.zone_id,
                        'student_count': cluster.student_count,
                        'schools': cluster.unique_schools
                    }
                })
            
            # Add zone centroid
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        zone.zone_centroid[1],  # lon
                        zone.zone_centroid[0]   # lat
                    ]
                },
                'properties': {
                    'type': 'zone_centroid',
                    'zone_id': zone.zone_id,
                    'total_students': zone.total_students,
                    'capacity_utilization': zone.capacity_utilization
                }
            })
        
        geojson = {
            'type': 'FeatureCollection',
            'features': features,
            'metadata': output.clustering_metrics
        }
        
        # Convert to native types for JSON serialization
        geojson = OutputFormatter._convert_to_native_types(geojson)
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(geojson, f, indent=2)
            print(f"\nVisualization data saved to: {filepath}")
        
        return geojson
