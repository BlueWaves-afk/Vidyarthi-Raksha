"""
Digital Twin Data Validation & Testing
Demonstrates the data engine and validates output quality.

Run this script to:
1. Generate a sample digital twin dataset
2. View summary statistics
3. Identify priority clusters
4. Export dataset for use in the dashboard
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.data_engine import (
    generate_digital_twin_dataset,
    get_dataset_summary,
    identify_priority_clusters,
    ENROLLMENT_CENTERS
)


def print_section(title: str, width: int = 80):
    """Print a formatted section header."""
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}\n")


def main():
    """Main validation routine."""
    
    print_section("DIGITAL TWIN DATA ENGINE - VALIDATION & DEMO")
    
    # ==========================================
    # 1. GENERATE DATASET
    # ==========================================
    print("📊 Generating Digital Twin Dataset (200 schools)...")
    df = generate_digital_twin_dataset(n_schools=200, seed=42)
    print(f"✓ Generated {len(df)} school records\n")
    
    # ==========================================
    # 2. DISPLAY SAMPLE RECORDS
    # ==========================================
    print_section("SAMPLE RECORDS (First 5 Schools)")
    print(df.head(5).to_string())
    
    # ==========================================
    # 3. SUMMARY STATISTICS
    # ==========================================
    print_section("DATASET SUMMARY STATISTICS")
    summary = get_dataset_summary(df)
    
    for key, value in summary.items():
        key_display = key.replace("_", " ").title()
        print(f"  {key_display:.<35} {value}")
    
    # ==========================================
    # 4. RURAL vs URBAN ANALYSIS
    # ==========================================
    print_section("RURAL vs URBAN ANALYSIS")
    
    rural_df = df[df["category"] == "rural"]
    urban_df = df[df["category"] == "urban"]
    
    print("RURAL SCHOOLS:")
    print(f"  Count:............................... {len(rural_df)}")
    print(f"  Avg Saturation:...................... {rural_df['saturation_rate'].mean():.3f}")
    print(f"  Avg Gender Parity Index (GPI):...... {rural_df['gender_parity_index'].mean():.3f}")
    print(f"  Equity Risk Schools:................ {rural_df['equity_risk'].sum()}")
    print(f"  Dark Zones:......................... {len(rural_df[rural_df['zone_label'] == 'Dark Zone'])}")
    print(f"  Avg Access Risk Score:............. {rural_df['access_risk_score'].mean():.1f}")
    
    print("\nURBAN SCHOOLS:")
    print(f"  Count:............................... {len(urban_df)}")
    print(f"  Avg Saturation:...................... {urban_df['saturation_rate'].mean():.3f}")
    print(f"  Avg Gender Parity Index (GPI):...... {urban_df['gender_parity_index'].mean():.3f}")
    print(f"  Equity Risk Schools:................ {urban_df['equity_risk'].sum()}")
    print(f"  Dark Zones:......................... {len(urban_df[urban_df['zone_label'] == 'Dark Zone'])}")
    print(f"  Avg Access Risk Score:............. {urban_df['access_risk_score'].mean():.1f}")
    
    # ==========================================
    # 5. ENROLLMENT CENTERS
    # ==========================================
    print_section("FIXED ENROLLMENT CENTERS")
    for center in ENROLLMENT_CENTERS:
        print(f"  {center['id']:.<20} {center['name']:.<25} ({center['lat']}, {center['lon']})")
    
    # ==========================================
    # 6. PRIORITY CLUSTERS
    # ==========================================
    print_section("TOP 10 PRIORITY SCHOOLS (Highest Intervention Urgency)")
    priority_df = identify_priority_clusters(df, top_n=10)
    
    for idx, row in priority_df.iterrows():
        print(f"\n  {row['school_id']} | {row['school_name']}")
        print(f"    Category:............... {row['category']}")
        print(f"    Backlog Students:....... {row['backlog_students']}")
        print(f"    Gender Parity Index:.... {row['gender_parity_index']:.3f}")
        print(f"    Equity Risk:............ {'YES' if row['equity_risk'] else 'NO'}")
        print(f"    Access Risk Score:...... {row['access_risk_score']:.1f}")
        print(f"    Priority Score:......... {row['priority_score']:.3f}")
    
    # ==========================================
    # 7. DATA DISTRIBUTION ANALYSIS
    # ==========================================
    print_section("DATA DISTRIBUTION ANALYSIS")
    
    print("BACKLOG DISTRIBUTION:")
    print(f"  Min:.............................. {df['backlog_students'].min()}")
    print(f"  Max:.............................. {df['backlog_students'].max()}")
    print(f"  Mean:............................. {df['backlog_students'].mean():.1f}")
    print(f"  Median:........................... {df['backlog_students'].median():.1f}")
    print(f"  Std Dev:.......................... {df['backlog_students'].std():.1f}")
    
    print("\nSATURATION RATE DISTRIBUTION:")
    print(f"  Min:.............................. {df['saturation_rate'].min():.3f}")
    print(f"  Max:.............................. {df['saturation_rate'].max():.3f}")
    print(f"  Mean:............................. {df['saturation_rate'].mean():.3f}")
    print(f"  Median:........................... {df['saturation_rate'].median():.3f}")
    
    print("\nGENDER PARITY INDEX (GPI) DISTRIBUTION:")
    print(f"  Min:.............................. {df['gender_parity_index'].min():.3f}")
    print(f"  Max:.............................. {df['gender_parity_index'].max():.3f}")
    print(f"  Mean:............................. {df['gender_parity_index'].mean():.3f}")
    gpi_low_risk = len(df[df['gender_parity_index'] < 0.9])
    print(f"  Schools with GPI < 0.9:.......... {gpi_low_risk} ({100*gpi_low_risk/len(df):.1f}%)")
    
    print("\nACCESS RISK SCORE DISTRIBUTION:")
    print(f"  Min:.............................. {df['access_risk_score'].min():.1f}")
    print(f"  Max:.............................. {df['access_risk_score'].max():.1f}")
    print(f"  Mean:............................. {df['access_risk_score'].mean():.1f}")
    
    # ==========================================
    # 8. ZONE BREAKDOWN
    # ==========================================
    print_section("ZONE CLASSIFICATION")
    
    zone_counts = df["zone_label"].value_counts()
    for zone, count in zone_counts.items():
        percentage = 100 * count / len(df)
        print(f"  {zone:.<30} {count:>3} schools ({percentage:>5.1f}%)")
    
    # ==========================================
    # 9. CRITICAL INSIGHTS
    # ==========================================
    print_section("CRITICAL INSIGHTS")
    
    high_backlog_equity = len(df[(df["backlog_students"] > df["backlog_students"].quantile(0.75)) & 
                                 (df["equity_risk"])])
    print(f"  Schools with HIGH backlog AND equity risk: {high_backlog_equity}")
    
    dark_zone_rural = len(df[(df["zone_label"] == "Dark Zone") & (df["category"] == "rural")])
    print(f"  Rural schools in Dark Zones: {dark_zone_rural}")
    
    low_saturation_cohort = len(df[df["saturation_rate"] < 0.5])
    print(f"  Schools with < 50% saturation: {low_saturation_cohort}")
    
    # ==========================================
    # 10. EXPORT DATASET
    # ==========================================
    print_section("EXPORTING DATASET")
    
    output_path = project_root / "data" / "digital_twin_schools.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✓ Exported to: {output_path}\n")
    
    print("=" * 80)
    print("  VALIDATION COMPLETE - Digital Twin Dataset Ready for Dashboard")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
