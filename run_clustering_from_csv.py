"""
Run bus clustering from CSV files.
Main script to execute clustering pipeline with CSV data.
"""
from csv_loader import CSVDataLoader
from src.clustering_pipeline import BusPoolingClusteringPipeline
from src.models.output import OutputFormatter


# Hardcoded file paths (update these to match your CSV locations)
STUDENTS_CSV = "barsha_students_synthetic (1).csv"
SCHOOLS_CSV = "barsha_schools_synthetic (1).csv"
ASSOCIATIONS_CSV = "student_school_association (1).csv"
ASSEMBLY_CSV = "assembly_points (1).csv"

# Output file path
OUTPUT_JSON = "clustering_output.json"
ROUTE_OPTIMIZER_JSON = "route_optimizer_input.json"


def main():
    """
    Main execution function.
    """
    print("\n" + "#"*80)
    print("# BUS POOLING CLUSTERING - CSV DATA PIPELINE")
    print("#"*80 + "\n")
    
    # Step 1: Load data from CSV files
    loader = CSVDataLoader(
        students_csv=STUDENTS_CSV,
        schools_csv=SCHOOLS_CSV,
        associations_csv=ASSOCIATIONS_CSV,
        assembly_csv=ASSEMBLY_CSV
    )
    
    students, assembly_points = loader.load_all()
    
    if not students:
        print("❌ Error: No students loaded. Check your CSV files and associations.")
        return
    
    if not assembly_points:
        print("❌ Error: No assembly points loaded. Check your assembly points CSV.")
        return
    
    # Step 2: Initialize clustering pipeline
    pipeline = BusPoolingClusteringPipeline(
        bus_capacity=50,                    # Adjust based on your bus size
        max_schools_per_zone=10,             # Allow buses to serve up to 3 schools
        school_proximity_threshold=1.0,     # Schools within 5km can share bus
        home_weight=0.7,                    # 60% weight to residential proximity
        school_weight=0.3,                  # 40% weight to school proximity
        max_walking_distance=1.0,           # Max 2km walking to assembly point
        use_pytorch_optimization=True,      # Enable PyTorch refinement
        optimization_epochs=500             # Optimization iterations
    )
    
    # Step 3: Run clustering
    print("\n" + "="*80)
    print("RUNNING CLUSTERING PIPELINE")
    print("="*80 + "\n")
    
    output = pipeline.run(
        students=students,
        assembly_points=assembly_points,
        verbose=True
    )
    
    # Step 4: Save outputs
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80 + "\n")
    
    # Save full clustering output
    formatter = OutputFormatter()
    formatter.to_json(output, filepath=OUTPUT_JSON)
    print(f"✓ Full clustering output saved to: {OUTPUT_JSON}")
    
    # Save route optimizer input format
    import json
    route_input = formatter.create_route_optimizer_input(output)
    route_input = formatter._convert_to_native_types(route_input)
    
    with open(ROUTE_OPTIMIZER_JSON, 'w') as f:
        json.dump(route_input, f, indent=2)
    print(f"✓ Route optimizer input saved to: {ROUTE_OPTIMIZER_JSON}")
    
    # Print final summary
    print("\n" + "="*80)
    print("CLUSTERING COMPLETE!")
    print("="*80)
    print(f"\n✓ Created {len(output.zones)} bus zones")
    print(f"✓ Total students clustered: {sum(z.total_students for z in output.zones)}")
    print(f"✓ Average capacity utilization: {sum(z.capacity_utilization for z in output.zones) / len(output.zones):.1%}")
    print(f"\nNext steps:")
    print(f"  1. Review {OUTPUT_JSON} for detailed zone assignments")
    print(f"  2. Pass {ROUTE_OPTIMIZER_JSON} to your route optimization module")
    print(f"  3. Visualize results using zone centroids and assembly points")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
