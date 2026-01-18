"""
Route Optimization Testing & Demonstration
Tests the RouteOptimizer with the Digital Twin dataset.

Run this to:
1. Generate test dataset
2. Optimize routes for various vehicle counts
3. View route details and efficiency metrics
4. Export optimized routes for dashboard visualization
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from core.data_engine import generate_digital_twin_dataset, get_dataset_summary
from core.optimization import RouteOptimizer, analyze_cluster_distribution, calculate_route_efficiency


def print_section(title: str, width: int = 90):
    """Print formatted section header."""
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}\n")


def main():
    """Main demonstration routine."""
    
    print_section("ROUTE OPTIMIZATION ENGINE - DEMONSTRATION & TESTING")
    
    # ==========================================
    # 1. GENERATE TEST DATASET
    # ==========================================
    print("📊 Generating Digital Twin Dataset...")
    df = generate_digital_twin_dataset(n_schools=200, seed=42)
    print(f"✓ Generated {len(df)} school records\n")
    
    # Display dataset summary
    summary = get_dataset_summary(df)
    print(f"  Total Backlog:................... {summary['total_backlog']:,} students")
    print(f"  Critical Schools:............... {summary['dark_zones']} in dark zones")
    print(f"  Equity Risk Schools:............ {summary['equity_risk_schools']}\n")
    
    # ==========================================
    # 2. INITIALIZE OPTIMIZER
    # ==========================================
    print_section("INITIALIZING OPTIMIZER")
    
    optimizer = RouteOptimizer(
        depot_lat=13.1939,
        depot_lon=77.5941,
        max_capacity=150,          # Students per vehicle per day
        max_time_minutes=480       # 8 hours per vehicle
    )
    
    print(f"  Depot Location:................. (13.1939, 77.5941)")
    print(f"  Vehicle Capacity:............... {optimizer.max_capacity} students/day")
    print(f"  Max Operating Time:............ {optimizer.max_time_minutes} minutes (8 hours)\n")
    
    # ==========================================
    # 3. CLUSTER DISTRIBUTION ANALYSIS
    # ==========================================
    print_section("CLUSTER DISTRIBUTION ANALYSIS")
    
    num_vehicles_scenarios = [3, 5, 8]
    
    for num_vehicles in num_vehicles_scenarios:
        print(f"  Scenario: {num_vehicles} Vehicles")
        cluster_analysis = analyze_cluster_distribution(df, num_vehicles)
        
        print(f"    Cluster Sizes:........... min={cluster_analysis['min_cluster_size']}, "
              f"avg={cluster_analysis['avg_cluster_size']:.1f}, max={cluster_analysis['max_cluster_size']}")
        print()
    
    # ==========================================
    # 4. ROUTE OPTIMIZATION (3 VEHICLES)
    # ==========================================
    print_section("ROUTE OPTIMIZATION (3 Mobile Units)")
    
    routes_3 = optimizer.optimize_routes(df, num_vehicles=3)
    
    print(f"  Routes Generated:.............. {len(routes_3)}")
    for route in routes_3:
        print(f"\n  {route['vehicle_id']}:")
        print(f"    Schools Visited:.......... {route['num_schools']}")
        print(f"    Students Enrolled:....... {route['total_students']}")
        print(f"    Distance:................ {route['total_distance_km']:.1f} km")
        print(f"    Time Required:........... {route['total_time_minutes']:.0f} min ({route['total_time_minutes']/60:.1f} hrs)")
        print(f"    Sample Schools:.......... {', '.join([s['school_id'] for s in route['schools'][:3]])}")
    
    # ==========================================
    # 5. ROUTE SUMMARY TABLE
    # ==========================================
    print_section("ROUTE EFFICIENCY METRICS (3 Vehicles)")
    
    summary_df = optimizer.get_route_summary()
    print(summary_df.to_string(index=False))
    
    # ==========================================
    # 6. EFFICIENCY ANALYSIS
    # ==========================================
    print_section("DETAILED EFFICIENCY ANALYSIS")
    
    efficiency_records = []
    for route in routes_3:
        efficiency = calculate_route_efficiency(route, optimizer.max_capacity, optimizer.max_time_minutes)
        efficiency_records.append(efficiency)
    
    efficiency_df = pd.DataFrame(efficiency_records)
    print(efficiency_df.to_string(index=False))
    
    avg_capacity_util = efficiency_df['capacity_utilization'].mean()
    avg_time_util = efficiency_df['time_utilization'].mean()
    
    print(f"\n  Average Capacity Utilization:.... {avg_capacity_util:.1f}%")
    print(f"  Average Time Utilization:........ {avg_time_util:.1f}%")
    print(f"  Overall Fleet Efficiency:....... {(avg_capacity_util + avg_time_util) / 2:.1f}%\n")
    
    # ==========================================
    # 7. ROUTE DETAILS & SCHOOL SEQUENCE
    # ==========================================
    print_section("DETAILED ROUTE SEQUENCE - VAN-001")
    
    van_001 = routes_3[0] if len(routes_3) > 0 else None
    if van_001:
        print(f"  Vehicle ID:.................... {van_001['vehicle_id']}")
        print(f"  Total Students:................ {van_001['total_students']}")
        print(f"  Total Distance:................ {van_001['total_distance_km']:.1f} km")
        print(f"  Total Time:.................... {van_001['total_time_minutes']:.0f} min\n")
        
        print("  School Sequence:")
        for idx, school in enumerate(van_001['schools']):
            print(f"    {idx+1}. {school['school_id']:10} | {school['school_name'][:40]:40} | "
                  f"Backlog: {school['backlog_students']:3} students")
    
    # ==========================================
    # 8. ROUTE COMPARISON (3 vs 5 vs 8 Vehicles)
    # ==========================================
    print_section("ROUTE OPTIMIZATION SCENARIOS")
    
    scenarios = []
    
    for num_vehicles in [3, 5, 8]:
        optimizer_temp = RouteOptimizer(
            max_capacity=150,
            max_time_minutes=480
        )
        routes = optimizer_temp.optimize_routes(df, num_vehicles=num_vehicles)
        
        total_students = sum(r['total_students'] for r in routes)
        total_distance = sum(r['total_distance_km'] for r in routes)
        num_schools = sum(r['num_schools'] for r in routes)
        
        scenarios.append({
            'num_vehicles': num_vehicles,
            'num_routes': len(routes),
            'num_schools_visited': num_schools,
            'total_students_enrolled': total_students,
            'total_distance_km': round(total_distance, 1),
            'avg_students_per_vehicle': round(total_students / len(routes), 1),
            'avg_distance_per_vehicle': round(total_distance / len(routes), 1),
        })
    
    scenario_df = pd.DataFrame(scenarios)
    print("\n" + scenario_df.to_string(index=False))
    
    # ==========================================
    # 9. COVERAGE ANALYSIS
    # ==========================================
    print_section("COVERAGE ANALYSIS")
    
    schools_with_backlog = len(df[df['backlog_students'] > 0])
    students_with_backlog = df[df['backlog_students'] > 0]['backlog_students'].sum()
    students_enrolled_3v = sum(r['total_students'] for r in routes_3)
    students_not_covered = students_with_backlog - students_enrolled_3v
    coverage_percentage = 100 * students_enrolled_3v / students_with_backlog if students_with_backlog > 0 else 0
    
    print(f"  Schools with Backlog:........... {schools_with_backlog}")
    print(f"  Total Backlog (students):....... {students_with_backlog:,}")
    print(f"  Enrolled (3 vehicles):.......... {students_enrolled_3v:,}")
    print(f"  Not Covered:.................... {students_not_covered:,}")
    print(f"  Coverage Percentage:............ {coverage_percentage:.1f}%\n")
    
    # ==========================================
    # 10. EXPORT ROUTES
    # ==========================================
    print_section("EXPORTING ROUTES")
    
    output_dir = project_root / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "optimized_routes_3vehicles.csv"
    optimizer.export_routes(str(output_file))
    
    # Also create a summary JSON-like export
    import json
    summary_file = output_dir / "route_summary.json"
    summary_export = {
        'optimization_date': pd.Timestamp.now().isoformat(),
        'num_vehicles': len(routes_3),
        'total_schools_visited': sum(r['num_schools'] for r in routes_3),
        'total_students_enrolled': sum(r['total_students'] for r in routes_3),
        'total_distance_km': sum(r['total_distance_km'] for r in routes_3),
        'routes': routes_3,
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary_export, f, indent=2, default=str)
    
    print(f"✓ Route details exported to {output_file}")
    print(f"✓ Summary exported to {summary_file}\n")
    
    # ==========================================
    # 11. KEY INSIGHTS
    # ==========================================
    print_section("KEY INSIGHTS & RECOMMENDATIONS")
    
    print("✓ STRENGTHS:")
    print(f"  - 3-vehicle fleet can cover {coverage_percentage:.0f}% of backlog")
    print(f"  - Average vehicle utilization: {avg_capacity_util:.0f}%")
    print(f"  - Cluster-first approach respects geographic proximity\n")
    
    print("⚠️  OBSERVATIONS:")
    if students_not_covered > 0:
        print(f"  - {students_not_covered:,} students remain unserved (consider 4-5 vehicles)")
    if avg_capacity_util < 70:
        print(f"  - Vehicle utilization is {avg_capacity_util:.0f}% (capacity underutilized)")
    if avg_time_util > 90:
        print(f"  - Time utilization is {avg_time_util:.0f}% (fleet may be overworked)\n")
    
    print("💡 RECOMMENDATIONS:")
    print("  - Deploy 5 vehicles for 90%+ coverage")
    print("  - Prioritize dark zone schools (access_risk_score > 75)")
    print("  - Schedule outreach campaigns during high-capacity periods")
    print("  - Monitor gender parity (equity_risk schools) closely\n")
    
    print("=" * 90)
    print("  OPTIMIZATION COMPLETE - Routes Ready for Dashboard Deployment")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
