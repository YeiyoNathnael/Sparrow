"""
Example usage script with multiple test scenarios.
Demonstrates different configurations and use cases.
"""
import numpy as np
from src.clustering_pipeline import BusPoolingClusteringPipeline
from src.utils.data_structures import Student, AssemblyPoint


def generate_test_data(scenario='urban'):
    """
    Generate test data for different scenarios.
    
    Args:
        scenario: 'urban' (high density), 'suburban' (medium), 'rural' (low density)
    
    Returns:
        Tuple of (students, assembly_points)
    """
    np.random.seed(42)
    
    if scenario == 'urban':
        n_students = 150
        n_assembly_points = 25
        n_schools = 8
        spread = 0.01  # Tight clustering
        
    elif scenario == 'suburban':
        n_students = 80
        n_assembly_points = 15
        n_schools = 5
        spread = 0.03  # Medium spread
        
    else:  # rural
        n_students = 40
        n_assembly_points = 10
        n_schools = 3
        spread = 0.05  # Wide spread
    
    # Base location (NYC coordinates)
    base_lat, base_lon = 40.7128, -74.0060
    
    # Generate school locations
    school_locations = []
    for i in range(n_schools):
        lat = base_lat + (i % 3) * spread * 2 + np.random.randn() * spread * 0.5
        lon = base_lon + (i // 3) * spread * 2 + np.random.randn() * spread * 0.5
        school_locations.append((lat, lon))
    
    # Generate students clustered in residential areas
    students = []
    n_clusters = max(5, n_students // 15)
    
    for i in range(n_students):
        cluster_id = i % n_clusters
        
        # Home location in residential cluster
        home_lat = base_lat + (cluster_id % 4) * spread * 1.5 + np.random.randn() * spread * 0.3
        home_lon = base_lon + (cluster_id // 4) * spread * 1.5 + np.random.randn() * spread * 0.3
        
        # Assign to school (some clustering, some mixing)
        if i % 3 == 0:
            # Some students from same area go to different schools
            school_idx = np.random.randint(0, n_schools)
        else:
            # Most students in area go to nearby schools
            school_idx = (cluster_id // 2) % n_schools
        
        school_id = f"school_{school_idx}"
        school_location = school_locations[school_idx]
        
        students.append(Student(
            student_id=f"student_{i:04d}",
            home_location=(home_lat, home_lon),
            school_id=school_id,
            school_location=school_location
        ))
    
    # Generate assembly points near residential clusters
    assembly_points = []
    for i in range(n_assembly_points):
        cluster_id = i % n_clusters
        
        # Place assembly points strategically in residential areas
        lat = base_lat + (cluster_id % 4) * spread * 1.5 + np.random.randn() * spread * 0.2
        lon = base_lon + (cluster_id // 4) * spread * 1.5 + np.random.randn() * spread * 0.2
        
        assembly_points.append(AssemblyPoint(
            assembly_id=f"assembly_{i:03d}",
            location=(lat, lon)
        ))
    
    return students, assembly_points


def run_scenario(scenario_name, students, assembly_points, config):
    """Run clustering for a specific scenario."""
    print("\n" + "="*80)
    print(f"SCENARIO: {scenario_name.upper()}")
    print("="*80)
    
    pipeline = BusPoolingClusteringPipeline(**config)
    output = pipeline.run(students, assembly_points, verbose=True)
    
    # Save output
    filename = f'output_{scenario_name}.json'
    pipeline.output_formatter.to_json(output, filepath=filename)
    
    return output


def main():
    """Run multiple test scenarios."""
    
    # Scenario 1: Urban high-density area
    print("\n" + "#"*80)
    print("# Scenario 1: Urban High-Density")
    print("#"*80)
    students, assembly_points = generate_test_data('urban')
    urban_output = run_scenario(
        'urban',
        students,
        assembly_points,
        config={
            'bus_capacity': 25,  # Larger buses in urban areas
            'max_schools_per_zone': 4,  # More schools per bus
            'home_weight': 0.7,  # Prioritize walking distance
            'school_weight': 0.3,
            'max_walking_distance': 1.0,  # Shorter walking distance
            'use_pytorch_optimization': True,
            'optimization_epochs': 50
        }
    )
    
    # Scenario 2: Suburban medium-density
    print("\n" + "#"*80)
    print("# Scenario 2: Suburban Medium-Density")
    print("#"*80)
    students, assembly_points = generate_test_data('suburban')
    suburban_output = run_scenario(
        'suburban',
        students,
        assembly_points,
        config={
            'bus_capacity': 20,  # Standard bus size
            'max_schools_per_zone': 3,
            'home_weight': 0.6,
            'school_weight': 0.4,
            'max_walking_distance': 1.5,
            'use_pytorch_optimization': True,
            'optimization_epochs': 100
        }
    )
    
    # Scenario 3: Rural low-density
    print("\n" + "#"*80)
    print("# Scenario 3: Rural Low-Density")
    print("#"*80)
    students, assembly_points = generate_test_data('rural')
    rural_output = run_scenario(
        'rural',
        students,
        assembly_points,
        config={
            'bus_capacity': 15,  # Smaller buses
            'max_schools_per_zone': 2,
            'home_weight': 0.5,  # Equal weight
            'school_weight': 0.5,
            'max_walking_distance': 3.0,  # Longer walking acceptable
            'use_pytorch_optimization': True,
            'optimization_epochs': 80
        }
    )
    
    # Comparison summary
    print("\n" + "="*80)
    print("SCENARIO COMPARISON")
    print("="*80)
    
    scenarios = [
        ('Urban', urban_output),
        ('Suburban', suburban_output),
        ('Rural', rural_output)
    ]
    
    print(f"\n{'Scenario':<15} {'Students':<12} {'Zones':<8} {'Avg/Zone':<12} {'Capacity%':<12} {'Silhouette':<12}")
    print("-" * 80)
    
    for name, output in scenarios:
        summary = output.to_dict()['summary']
        metrics = output.clustering_metrics
        
        print(f"{name:<15} "
              f"{summary['total_students']:<12} "
              f"{summary['total_zones']:<8} "
              f"{summary['avg_students_per_zone']:<12.1f} "
              f"{summary['avg_capacity_utilization']*100:<12.1f} "
              f"{metrics.get('silhouette_score', 0):<12.3f}")
    
    print("\n" + "="*80)
    print("All scenarios completed! Check output_*.json files for details.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
