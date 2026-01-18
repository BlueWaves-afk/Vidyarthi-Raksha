import pandas as pd
import numpy as np
import random

def generate_data(num_schools=100):
    print("🔄 Generating synthetic government school data...")

    # Center coordinates (Bangalore Rural context)
    base_lat = 13.20
    base_lon = 77.55

    # Initialize containers (FIXED)
    schools_data = []

    # List of realistic school prefixes to make data look authentic (FIXED)
    prefixes = [
        "Govt High School",
        "Govt Primary School",
        "Zilla Parishad School",
        "Model Govt School",
        "Adarsha Vidyalaya"
    ]

    towns = [
        "Devanahalli",
        "Doddaballapur",
        "Hoskote",
        "Nelamangala",
        "Magadi",
        "Ramanagara"
    ]

    for i in range(1, num_schools + 1):
        # 1. Create Realistic Location (Clustered)
        lat_offset = random.uniform(-0.08, 0.08)
        lon_offset = random.uniform(-0.08, 0.08)

        # 2. Generate Core Metrics
        # Backlog: How many students need updates (10 to 300)
        if random.random() < 0.2:
            backlog = random.randint(150, 400)
        else:
            backlog = random.randint(10, 80)

        # Gender Parity Index (GPI)
        gpi = round(random.uniform(0.65, 1.1), 2)

        # 3. Calculate Priority Score
        norm_backlog = min(backlog / 400, 1.0)
        risk_gpi = max(0, 1.0 - gpi)

        priority_score = (norm_backlog * 0.7) + (risk_gpi * 0.3)
        priority_score = round(priority_score, 2)

        # 4. Determine Status
        if priority_score > 0.4 or backlog > 150:
            status = "CRITICAL"
        else:
            status = "NORMAL"

        school = {
            "school_id": f"SCH-{1000+i}",
            "school_name": f"{random.choice(prefixes)}, {random.choice(towns)} Block-{random.randint(1,9)}",
            "latitude": round(base_lat + lat_offset, 6),
            "longitude": round(base_lon + lon_offset, 6),
            "backlog_students": backlog,
            "gender_parity_index": gpi,
            "priority_score": priority_score,
            "status": status,
            "contact_number": f"+91-98{random.randint(10000000, 99999999)}"
        }

        schools_data.append(school)

    # Create DataFrame
    df = pd.DataFrame(schools_data)

    # Save to CSV
    filename = "mock_school_data.csv"
    df.to_csv(filename, index=False)

    print(f"✅ Success! Generated {filename} with {num_schools} schools.")
    print(f" - Critical Schools: {len(df[df['status']=='CRITICAL'])}")
    print(f" - Columns: {list(df.columns)}")

if __name__ == "__main__":
    generate_data()
