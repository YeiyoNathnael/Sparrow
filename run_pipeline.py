"""
Unified Pipeline Runner

This script runs the complete bus routing pipeline:
1. Loads CSV data based on config/datasets.yaml
2. Runs clustering to create bus zones
3. Runs route optimization (RL4CO)
4. Updates the backend database
5. Restarts the backend server

Usage:
    python run_pipeline.py                    # Run full pipeline
    python run_pipeline.py --cluster-only     # Only run clustering
    python run_pipeline.py --optimize-only    # Only run route optimization
    python run_pipeline.py --preset <name>    # Use a preset dataset
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# Try to import yaml, fall back to basic parsing if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("⚠️  PyYAML not installed. Install with: pip install pyyaml")


def load_config(config_path: str = "config/datasets.yaml") -> dict:
    """Load configuration from YAML file."""
    if not HAS_YAML:
        # Fallback: return default config
        return {
            'active_dataset': {
                'name': 'Al Barsha Dubai (Synthetic)',
                'students_csv': 'barsha_students_synthetic (1).csv',
                'schools_csv': 'barsha_schools_synthetic (1).csv',
                'associations_csv': 'student_school_association (1).csv',
                'assembly_points_csv': 'assembly_points (1).csv',
                'map_center': {'latitude': 25.0950, 'longitude': 55.2200},
                'region': 'Al Barsha, Dubai, UAE'
            },
            'clustering': {
                'bus_capacity': 50,
                'max_schools_per_zone': 10,
                'school_proximity_threshold': 1.0,
                'home_weight': 0.7,
                'school_weight': 0.3,
                'max_walking_distance': 1.0,
                'use_pytorch_optimization': True,
                'optimization_epochs': 500
            },
            'output': {
                'clustering_json': 'clustering_output.json',
                'route_optimizer_input': 'route_optimizer_input.json',
                'optimized_routes': 'optimized_routes.json'
            }
        }
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def validate_csv_files(config: dict) -> bool:
    """Check that all required CSV files exist."""
    dataset = config['active_dataset']
    files = [
        dataset['students_csv'],
        dataset['schools_csv'],
        dataset['associations_csv'],
        dataset['assembly_points_csv']
    ]
    
    all_exist = True
    for filepath in files:
        if os.path.exists(filepath):
            print(f"  ✓ Found: {filepath}")
        else:
            print(f"  ✗ Missing: {filepath}")
            all_exist = False
    
    return all_exist


def run_clustering(config: dict) -> bool:
    """Run the clustering pipeline."""
    print("\n" + "="*60)
    print("STEP 1: CLUSTERING PIPELINE")
    print("="*60)
    
    dataset = config['active_dataset']
    clustering = config['clustering']
    output = config['output']
    
    # Import clustering modules
    from csv_loader import CSVDataLoader
    from src.clustering_pipeline import BusPoolingClusteringPipeline
    from src.models.output import OutputFormatter
    
    # Load data
    print(f"\n📂 Loading dataset: {dataset['name']}")
    loader = CSVDataLoader(
        students_csv=dataset['students_csv'],
        schools_csv=dataset['schools_csv'],
        associations_csv=dataset['associations_csv'],
        assembly_csv=dataset['assembly_points_csv']
    )
    
    students, assembly_points = loader.load_all()
    
    if not students:
        print("❌ Error: No students loaded")
        return False
    
    if not assembly_points:
        print("❌ Error: No assembly points loaded")
        return False
    
    print(f"  ✓ Loaded {len(students)} students")
    print(f"  ✓ Loaded {len(assembly_points)} assembly points")
    
    # Initialize pipeline
    pipeline = BusPoolingClusteringPipeline(
        bus_capacity=clustering['bus_capacity'],
        max_schools_per_zone=clustering['max_schools_per_zone'],
        school_proximity_threshold=clustering['school_proximity_threshold'],
        home_weight=clustering['home_weight'],
        school_weight=clustering['school_weight'],
        max_walking_distance=clustering['max_walking_distance'],
        use_pytorch_optimization=clustering['use_pytorch_optimization'],
        optimization_epochs=clustering['optimization_epochs']
    )
    
    # Run clustering
    print("\n🔄 Running clustering...")
    result = pipeline.run(students=students, assembly_points=assembly_points, verbose=True)
    
    # Save outputs
    formatter = OutputFormatter()
    formatter.to_json(result, filepath=output['clustering_json'])
    print(f"  ✓ Saved: {output['clustering_json']}")
    
    # Save route optimizer input
    route_input = formatter.create_route_optimizer_input(result)
    route_input = formatter._convert_to_native_types(route_input)
    
    with open(output['route_optimizer_input'], 'w') as f:
        json.dump(route_input, f, indent=2)
    print(f"  ✓ Saved: {output['route_optimizer_input']}")
    
    print(f"\n✅ Clustering complete: {len(result.zones)} bus zones created")
    return True


def run_route_optimization(config: dict) -> bool:
    """Run the route optimization pipeline."""
    print("\n" + "="*60)
    print("STEP 2: ROUTE OPTIMIZATION (RL4CO)")
    print("="*60)
    
    output = config['output']
    input_file = output['route_optimizer_input']
    output_file = output['optimized_routes']
    
    if not os.path.exists(input_file):
        print(f"❌ Missing input file: {input_file}")
        print("   Run clustering first with: python run_pipeline.py --cluster-only")
        return False
    
    # Import and run route optimizer
    print(f"\n📂 Loading zones from: {input_file}")
    
    try:
        from src.models.route_optimizer import RL4CORouteOptimizer
        import torch
        
        with open(input_file, 'r') as f:
            route_data = json.load(f)
        
        # Handle both 'routes' and 'zones' keys for compatibility
        if 'routes' in route_data:
            num_routes = len(route_data['routes'])
        elif 'zones' in route_data:
            num_routes = len(route_data['zones'])
            # Convert old format to new format
            route_data['routes'] = route_data['zones']
        else:
            raise KeyError("Input JSON must have 'routes' or 'zones' key")
        
        print(f"  ✓ Loaded {num_routes} routes/zones")
        
        # Initialize optimizer with appropriate device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        optimizer = RL4CORouteOptimizer(device=device)
        
        # Run optimization
        print("\n🔄 Optimizing routes...")
        routes = optimizer.optimize_routes(route_data)
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(routes, f, indent=2)
        print(f"  ✓ Saved: {output_file}")
        
        # Summary
        total_distance = sum(r['distance_km'] for r in routes.values())
        print(f"\n✅ Route optimization complete:")
        print(f"   • {len(routes)} routes optimized")
        print(f"   • Total distance: {total_distance:.2f} km")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure RL4CO is installed: pip install rl4co")
        return False
    except Exception as e:
        print(f"❌ Optimization error: {e}")
        return False


def update_backend_database(config: dict) -> bool:
    """Reload routes into the backend database."""
    print("\n" + "="*60)
    print("STEP 3: UPDATE BACKEND DATABASE")
    print("="*60)
    
    output = config['output']
    routes_file = output['optimized_routes']
    
    if not os.path.exists(routes_file):
        print(f"❌ Missing routes file: {routes_file}")
        return False
    
    # The backend auto-loads from optimized_routes.json on startup
    # We just need to verify the file is valid
    try:
        with open(routes_file, 'r') as f:
            routes = json.load(f)
        print(f"  ✓ Verified {len(routes)} routes in {routes_file}")
        print("\n💡 Restart the backend to load new routes:")
        print("   cd backend && python main.py")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {routes_file}: {e}")
        return False


def update_frontend_config(config: dict) -> bool:
    """Update frontend map center based on dataset config."""
    print("\n" + "="*60)
    print("STEP 4: UPDATE FRONTEND CONFIG")
    print("="*60)
    
    dataset = config['active_dataset']
    map_center = dataset.get('map_center', {})
    
    if not map_center:
        print("⚠️  No map_center in config, skipping frontend update")
        return True
    
    lat = map_center.get('latitude', 25.0950)
    lng = map_center.get('longitude', 55.2200)
    
    livemap_path = "frontend/src/pages/LiveMap.tsx"
    
    if not os.path.exists(livemap_path):
        print(f"⚠️  Frontend file not found: {livemap_path}")
        return True
    
    # Read current file
    with open(livemap_path, 'r') as f:
        content = f.read()
    
    # Update map center constant
    import re
    pattern = r'const AL_BARSHA_CENTER: \[number, number\] = \[\d+\.\d+, \d+\.\d+\];'
    replacement = f'const AL_BARSHA_CENTER: [number, number] = [{lat}, {lng}];'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(livemap_path, 'w') as f:
            f.write(new_content)
        print(f"  ✓ Updated map center to [{lat}, {lng}]")
    else:
        print(f"  ✓ Map center already set to [{lat}, {lng}]")
    
    print(f"\n💡 Rebuild frontend to apply changes:")
    print(f"   cd frontend && npm run build")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Run the bus routing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                    # Run full pipeline
  python run_pipeline.py --cluster-only     # Only clustering
  python run_pipeline.py --optimize-only    # Only route optimization
  python run_pipeline.py --validate         # Just validate CSV files
        """
    )
    
    parser.add_argument('--cluster-only', action='store_true',
                        help='Only run clustering step')
    parser.add_argument('--optimize-only', action='store_true',
                        help='Only run route optimization step')
    parser.add_argument('--validate', action='store_true',
                        help='Only validate CSV files exist')
    parser.add_argument('--config', type=str, default='config/datasets.yaml',
                        help='Path to config file')
    parser.add_argument('--preset', type=str,
                        help='Use a preset dataset from config')
    
    args = parser.parse_args()
    
    print("\n" + "#"*60)
    print("#  BUS ROUTING PIPELINE")
    print("#"*60)
    
    # Load config
    print(f"\n📋 Loading config from: {args.config}")
    config = load_config(args.config)
    
    # Handle preset selection
    if args.preset:
        presets = config.get('presets', {})
        if args.preset in presets:
            config['active_dataset'] = presets[args.preset]
            print(f"  ✓ Using preset: {args.preset}")
        else:
            print(f"❌ Unknown preset: {args.preset}")
            print(f"   Available presets: {list(presets.keys())}")
            sys.exit(1)
    
    dataset = config['active_dataset']
    print(f"\n📊 Active Dataset: {dataset['name']}")
    print(f"   Region: {dataset.get('region', 'Unknown')}")
    
    # Validate files
    print("\n🔍 Checking CSV files...")
    if not validate_csv_files(config):
        print("\n❌ Missing CSV files. Please check your config.")
        sys.exit(1)
    
    if args.validate:
        print("\n✅ All CSV files found!")
        sys.exit(0)
    
    # Run pipeline steps
    success = True
    
    if not args.optimize_only:
        success = run_clustering(config) and success
    
    if not args.cluster_only and success:
        success = run_route_optimization(config) and success
    
    if success:
        success = update_backend_database(config) and success
        success = update_frontend_config(config) and success
    
    # Final summary
    print("\n" + "="*60)
    if success:
        print("✅ PIPELINE COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Restart backend:  cd backend && python main.py")
        print("  2. Rebuild frontend: cd frontend && npm run build && npm run dev")
        print("  3. Open browser:     http://localhost:8080")
    else:
        print("❌ PIPELINE FAILED")
        print("="*60)
        print("\nCheck the errors above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
