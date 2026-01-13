import pandas as pd
import random

# Generate 50 dummy schools in a specific district (e.g., Bangalore Rural)
def generate_data():
    data = []  # FIXED: properly indented

    # Approx Lat/Lon for Bangalore Rural
    base_lat = 13.2
    base_lon = 77.5

    zones = ["North", "South", "East", "West", "Central"]

    for i in range(1, 51):
        # Random coordinates (~10 km radius)
        school_lat = base_lat + random.uniform(-0.05, 0.05)
        school_lon = base_lon + random.uniform(-0.05, 0.05)

        # Random student count
        total_students = random.randint(100, 500)

        # 30% high‑risk schools
        if random.random() < 0.3:
            pending_mbu = random.randint(50, 150)
            risk_level = "High"
        else:
            pending_mbu = random.randint(0, 20)
            risk_level = "Low"

        school = {
            "school_id": f"SCH-{1000 + i}",
            "school_name": f"Govt High School, Zone {random.choice(zones)} - {i}",
            "lat": round(school_lat, 6),
            "lon": round(school_lon, 6),
            "total_students": total_students,
            "pending_mbu": pending_mbu,
            "risk_level": risk_level
        }

        data.append(school)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv("mock_school_data.csv", index=False)

    print("✅ Success! Generated 'mock_school_data.csv' with 50 schools.")
    print(df.head())

if __name__ == "__main__":
    generate_data()
