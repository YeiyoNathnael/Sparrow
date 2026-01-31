"""
Run route optimization using RL4CO on clustering output.

This script:
1. Loads the route_optimizer_input.json from clustering pipeline
2. Optimizes each route using POMO (two-phase: pickups then dropoffs)
3. Outputs optimized_routes.json with coordinate sequences
"""

import json
import os
from pathlib import Path
import torch

from src.models.route_optimizer import RL4CORouteOptimizer


# File paths
BASE_DIR = Path(__file__).parent
INPUT_JSON = BASE_DIR / 'route_optimizer_input.json'
OUTPUT_JSON = BASE_DIR / 'optimized_routes.json'


def main():
    """Main execution function."""
    
    print("=" * 60)
    print("ROUTE OPTIMIZATION WITH RL4CO (POMO)")
    print("=" * 60)
    
    # Check if input file exists
    if not INPUT_JSON.exists():
        print(f"\n❌ Error: Input file not found: {INPUT_JSON}")
        print("\nPlease run the clustering pipeline first:")
        print("  python run_clustering_from_csv.py")
        return
    
    # Load clustering output
    print(f"\n📂 Loading clustering output from: {INPUT_JSON}")
    with open(INPUT_JSON, 'r') as f:
        route_input = json.load(f)
    
    num_routes = len(route_input.get('routes', []))
    print(f"   Found {num_routes} routes to optimize")
    
    # Initialize optimizer
    print("\n🤖 Initializing RL4CO POMO optimizer...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"   Using device: {device}")
    
    optimizer = RL4CORouteOptimizer(
        device=device,
        depot_strategy='centroid',  # Use zone centroid as depot
        depot_location=None
    )
    
    # Optimize all routes
    print("\n🚌 Optimizing routes...")
    print("   Strategy: Two-phase (pickups → dropoffs)")
    print("   Model: POMO (Policy Optimization with Multiple Optima)")
    print()
    
    optimized_routes = optimizer.optimize_routes(route_input)
    
    # Display results
    print("\n" + "=" * 60)
    print("OPTIMIZATION RESULTS")
    print("=" * 60)
    
    total_distance = 0.0
    for bus_id, route_data in sorted(optimized_routes.items()):
        num_stops = len(route_data['stops'])
        distance = route_data['distance_km']
        num_pickups = route_data['num_pickups']
        num_dropoffs = route_data['num_dropoffs']
        
        print(f"\n{bus_id}:")
        print(f"  Stops: {num_stops} ({num_pickups} pickups + {num_dropoffs} dropoffs + 1 depot)")
        print(f"  Distance: {distance} km")
        print(f"  Depot: [{route_data['depot'][0]:.6f}, {route_data['depot'][1]:.6f}]")
        
        total_distance += distance
    
    avg_distance = total_distance / len(optimized_routes) if optimized_routes else 0
    print(f"\n{'─' * 60}")
    print(f"Total distance: {total_distance:.2f} km")
    print(f"Average per route: {avg_distance:.2f} km")
    print(f"{'─' * 60}")
    
    # Save optimized routes
    print(f"\n💾 Saving optimized routes to: {OUTPUT_JSON}")
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(optimized_routes, f, indent=2)
    
    print("\n✅ Route optimization complete!")
    print("\nOutput format:")
    print('  {')
    print('    "bus_0": {')
    print('      "stops": [[lat, lon], [lat, lon], ...],')
    print('      "depot": [lat, lon],')
    print('      "distance_km": float,')
    print('      "num_pickups": int,')
    print('      "num_dropoffs": int')
    print('    },')
    print('    ...')
    print('  }')
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
