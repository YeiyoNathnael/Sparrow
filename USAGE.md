# Usage Guide

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Your Data

Your input data should include:

**Students** - Each student object must have:
- `student_id`: Unique identifier (string)
- `home_location`: Tuple of (latitude, longitude)
- `school_id`: School identifier (string)
- `school_location`: Tuple of (latitude, longitude)

**Assembly Points** - Predefined pickup locations:
- `assembly_id`: Unique identifier (string)
- `location`: Tuple of (latitude, longitude)

### 3. Run Clustering

```python
from src.clustering_pipeline import BusPoolingClusteringPipeline
from src.utils.data_structures import Student, AssemblyPoint

# Create students
students = [
    Student(
        student_id="s001",
        home_location=(40.7128, -74.0060),
        school_id="school_A",
        school_location=(40.7589, -73.9851)
    ),
    # ... add more students
]

# Create assembly points
assembly_points = [
    AssemblyPoint(
        assembly_id="a001",
        location=(40.7150, -74.0070)
    ),
    # ... add more assembly points
]

# Initialize and run pipeline
pipeline = BusPoolingClusteringPipeline(
    bus_capacity=20,           # Students per bus
    max_schools_per_zone=3,    # Max schools per bus
    home_weight=0.6,           # Weight for home proximity
    school_weight=0.4          # Weight for school proximity
)

output = pipeline.run(students, assembly_points, verbose=True)
```

### 4. Access Results

```python
# Get zones
for zone in output.zones:
    print(f"Zone {zone.zone_id}:")
    print(f"  Students: {zone.total_students}")
    print(f"  Assembly points: {zone.assembly_point_ids}")
    print(f"  Schools: {zone.school_ids}")

# Get as dictionary
output_dict = output.to_dict()

# Save to JSON
from src.models.output import OutputFormatter
formatter = OutputFormatter()
formatter.to_json(output, filepath='results.json')

# Create input for route optimizer
route_input = formatter.create_route_optimizer_input(output)
```

## Input from Dictionary

If you have data in dictionary format:

```python
input_data = {
    'students': [
        {
            'student_id': 's001',
            'home_location': [40.7128, -74.0060],
            'school_id': 'school_A',
            'school_location': [40.7589, -73.9851]
        },
        # ... more students
    ],
    'assembly_points': [
        {
            'assembly_id': 'a001',
            'location': [40.7150, -74.0070]
        },
        # ... more assembly points
    ],
    'n_zones': 5  # Optional: number of buses
}

output = pipeline.run_from_dict(input_data, verbose=True)
```

## Configuration Options

### Pipeline Parameters

```python
pipeline = BusPoolingClusteringPipeline(
    # Capacity constraints
    bus_capacity=20,                    # Max students per bus
    
    # School constraints
    max_schools_per_zone=3,             # Max different schools per bus
    school_proximity_threshold=5.0,     # Max km between schools (km)
    
    # Distance weighting
    home_weight=0.6,                    # Weight for residential proximity
    school_weight=0.4,                  # Weight for school proximity
    
    # Walking distance
    max_walking_distance=2.0,           # Max walk to assembly point (km)
    
    # Optimization
    use_pytorch_optimization=True,      # Enable gradient-based refinement
    optimization_epochs=100             # Number of optimization iterations
)
```

### Weight Tuning Guidelines

**Urban areas** (high density):
- `home_weight=0.7, school_weight=0.3` - Prioritize short walking distances
- `max_walking_distance=1.0` km
- `bus_capacity=25` - Larger buses

**Suburban areas** (medium density):
- `home_weight=0.6, school_weight=0.4` - Balanced
- `max_walking_distance=1.5` km
- `bus_capacity=20` - Standard buses

**Rural areas** (low density):
- `home_weight=0.5, school_weight=0.5` - Equal weight
- `max_walking_distance=3.0` km
- `bus_capacity=15` - Smaller buses

## Output Format

### Zone Structure

```json
{
  "zone_id": 0,
  "assembly_nodes": ["a001", "a003", "a007"],
  "schools": ["school_A", "school_B"],
  "student_count": 18,
  "capacity": 20,
  "capacity_utilization": 0.9,
  "school_distribution": {
    "school_A": 10,
    "school_B": 8
  },
  "zone_centroid": [40.7128, -74.0060],
  "home_centroid": [40.7125, -74.0062],
  "school_centroid": [40.7580, -73.9850]
}
```

### Route Optimizer Input

```python
route_input = formatter.create_route_optimizer_input(output)

# Structure:
{
  "routes": [
    {
      "route_id": 0,
      "capacity": 20,
      "total_students": 18,
      "pickup_nodes": [
        {
          "node_id": "a001",
          "type": "pickup",
          "location": {"lat": 40.7128, "lon": -74.0060},
          "demand": 6,
          "students": ["s001", "s002", ...]
        }
      ],
      "dropoff_nodes": [
        {
          "node_id": "school_A",
          "type": "dropoff",
          "location": {"lat": 40.7589, "lon": -73.9851},
          "students_to_drop": ["s001", "s005", ...]
        }
      ]
    }
  ]
}
```

## Metrics

Access clustering quality metrics:

```python
metrics = output.clustering_metrics

# Key metrics:
print(f"Silhouette score: {metrics['silhouette_score']}")  # Cluster quality
print(f"Avg walking distance: {metrics['avg_walking_distance_km']} km")
print(f"Capacity utilization: {metrics['avg_capacity_utilization']:.1%}")
print(f"Schools per zone: {metrics['avg_schools_per_zone']}")
```

## Examples

Run example scenarios:

```bash
# Basic example
python src/clustering_pipeline.py

# Multiple scenarios (urban, suburban, rural)
python examples.py
```

## Troubleshooting

**Issue**: "Zones over capacity"
- **Solution**: Increase `bus_capacity` or add more buses (decrease students per zone)

**Issue**: "High walking distances"
- **Solution**: Add more assembly points or increase `max_walking_distance`

**Issue**: "Too many schools per zone"
- **Solution**: Decrease `max_schools_per_zone` or increase `school_weight`

**Issue**: "Poor clustering quality (low silhouette)"
- **Solution**: Adjust `home_weight`/`school_weight` balance or enable PyTorch optimization

## API Reference

See inline documentation in source files:
- `src/clustering_pipeline.py` - Main pipeline
- `src/models/` - Clustering algorithms
- `src/utils/` - Utilities and data structures
