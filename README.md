# Bus Pooling Clustering System

A PyTorch-based clustering system for optimizing school bus routes through intelligent student grouping. The system clusters students attending different schools into shared bus zones based on residential proximity and destination similarity.

## Overview

This system solves the multi-school bus pooling problem by:
1. **Assigning students to assembly points** - Groups students to nearest pickup locations based on home addresses
2. **Clustering assembly points into bus zones** - Creates bus routes considering both home proximity (60%) and school proximity (40%)
3. **PyTorch optimization** - Refines clusters using gradient-based optimization with capacity constraints

## Features

- ✅ **Haversine distance computation** for accurate geo-spatial calculations
- ✅ **Capacity-constrained k-means** clustering with configurable bus capacity
- ✅ **Multi-school support** - Buses can serve 2-3 schools if they're within threshold distance
- ✅ **Differentiable soft clustering** using Gumbel-Softmax for gradient-based optimization
- ✅ **Comprehensive metrics** - Silhouette score, capacity utilization, walking distances, cluster quality
- ✅ **Flexible output formats** - JSON, route optimizer input, GeoJSON for visualization

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from src.clustering_pipeline import BusPoolingClusteringPipeline
from src.utils.data_structures import Student, AssemblyPoint

# Define students
students = [
    Student(
        student_id="student_001",
        home_location=(40.7128, -74.0060),  # (lat, lon)
        school_id="school_A",
        school_location=(40.7589, -73.9851)
    ),
    # ... more students
]

# Define assembly points (predefined pickup locations)
assembly_points = [
    AssemblyPoint(
        assembly_id="assembly_01",
        location=(40.7150, -74.0070)
    ),
    # ... more assembly points
]

# Run clustering pipeline
pipeline = BusPoolingClusteringPipeline(
    bus_capacity=20,
    max_schools_per_zone=3,
    home_weight=0.6,
    school_weight=0.4
)

output = pipeline.run(students, assembly_points, verbose=True)

# Save results
pipeline.output_formatter.to_json(output, filepath='results.json')
```

## Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `bus_capacity` | 20 | Maximum students per bus |
| `max_schools_per_zone` | 3 | Max different schools per bus |
| `school_proximity_threshold` | 5.0 km | Max distance between schools in same zone |
| `home_weight` | 0.6 | Weight for residential proximity |
| `school_weight` | 0.4 | Weight for school destination proximity |
| `max_walking_distance` | 2.0 km | Max walking distance to assembly point |
| `use_pytorch_optimization` | True | Enable gradient-based refinement |
| `optimization_epochs` | 100 | Number of optimization iterations |

## Project Structure

```
jack-sparrow/
├── src/
│   ├── models/
│   │   ├── student_assignment.py    # Stage 1: Student → Assembly
│   │   ├── zone_clustering.py       # Stage 2: Assembly → Zones
│   │   ├── pytorch_optimizer.py     # Stage 3: PyTorch refinement
│   │   └── output.py                # Output formatting
│   ├── utils/
│   │   ├── distance.py              # Haversine distance calculations
│   │   ├── data_structures.py       # Core data classes
│   │   └── metrics.py               # Clustering quality metrics
│   └── clustering_pipeline.py       # Main entry point
├── requirements.txt
└── README.md
```

## Output Format

The system produces structured output with zones containing:

```json
{
  "zones": [
    {
      "zone_id": 0,
      "assembly_nodes": ["assembly_01", "assembly_03"],
      "schools": ["school_A", "school_B"],
      "student_count": 18,
      "capacity": 20,
      "capacity_utilization": 0.9,
      "school_distribution": {"school_A": 10, "school_B": 8},
      "zone_centroid": [40.7128, -74.0060]
    }
  ],
  "metrics": {
    "silhouette_score": 0.65,
    "avg_walking_distance_km": 0.42,
    "avg_capacity_utilization": 0.85
  }
}
```

## Running the Example

```bash
python src/clustering_pipeline.py
```

This generates synthetic data (100 students, 15 assembly points, 5 schools) and demonstrates the full pipeline.

## Algorithm Details

### Stage 1: Student Assignment
- Uses batch Haversine distance computation with PyTorch
- Assigns each student to nearest assembly point
- Time complexity: O(N × M) where N=students, M=assembly points

### Stage 2: Zone Clustering
- K-means++ initialization for better convergence
- Capacity-constrained assignment using greedy algorithm
- Combined distance metric: 0.6×home_distance + 0.4×school_distance
- Time complexity: O(I × K × M) where I=iterations, K=zones

### Stage 3: PyTorch Optimization
- Differentiable soft clustering with Gumbel-Softmax
- Multi-objective loss: distance + capacity penalty + balance + compactness
- Adam optimizer with learnable temperature parameter
- Time complexity: O(E × K × M) where E=epochs

## Metrics Computed

- **Distance metrics**: Walking distances, zone compactness
- **Cluster quality**: Silhouette score, intra/inter-cluster distances  
- **Capacity metrics**: Utilization, balance, violations
- **School distribution**: Schools per zone, diversity penalty

## Next Steps

This clustering module outputs assembly nodes and zones for downstream route optimization. The next module should:
1. Take the zone/assembly assignments
2. Optimize actual route sequences (TSP/VRP)
3. Consider time windows and traffic patterns
4. Generate turn-by-turn directions

## License

MIT
