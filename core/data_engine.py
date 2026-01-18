"""
Digital Twin Data Engine
Generates high-fidelity synthetic datasets simulating "invisible backlog" 
and rural/urban disparities for Aadhaar enrollment optimization.

Key Concepts:
- Age-15 Cohort: 8-10% of total student population (target for enrollment)
- Saturation Rate: Beta-distributed enrollment coverage (α=5, β=2)
- Rural Penalty: 0.15 factor applied to rural schools (access barriers)
- Gender Parity Index (GPI): Female/Male saturation ratio
- Equity Risk: Flagged when GPI < 0.9
- Access Risk: Distance-based scoring (0-100) from fixed enrollment centers
- Dark Zones: Schools with access_risk_score > 75
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, List, Dict


# ==========================================
# 1. FIXED ENROLLMENT CENTERS
# ==========================================
# Simulates 5 major enrollment hubs (assume Karnataka/Bengaluru region)
ENROLLMENT_CENTERS = [
    {"id": "CENTER_1", "lat": 13.1939, "lon": 77.5941, "name": "Bengaluru Central"},
    {"id": "CENTER_2", "lat": 13.0827, "lon": 77.6254, "name": "Whitefield Hub"},
    {"id": "CENTER_3", "lat": 13.1959, "lon": 77.7049, "name": "Indiranagar"},
    {"id": "CENTER_4", "lat": 12.9352, "lon": 77.6245, "name": "Electronic City"},
    {"id": "CENTER_5", "lat": 13.2328, "lon": 77.4597, "name": "Devanahalli"},
]


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two points (lat, lon) in kilometers.
    
    Args:
        lat1, lon1: School coordinates
        lat2, lon2: Center coordinates
    
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in kilometers
    
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    
    a = np.sin(delta_lat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c


def is_rural(lat: float, lon: float, urban_core_lat: float = 13.1939, urban_core_lon: float = 77.5941) -> bool:
    """
    Classify school as rural or urban based on distance from urban core (Bengaluru).
    
    Schools > 25 km from urban center are classified as rural.
    
    Args:
        lat, lon: School coordinates
        urban_core_lat, urban_core_lon: Urban center reference point
    
    Returns:
        True if rural, False if urban
    """
    distance = haversine_distance(lat, lon, urban_core_lat, urban_core_lon)
    return distance > 25


def calculate_cohort_backlog(total_students: int, cohort_percentage: float = None) -> int:
    """
    Estimate age-15 cohort size (target enrollment group).
    
    Args:
        total_students: Total school enrollment
        cohort_percentage: Percentage of students in age-15 cohort (default: random 8-10%)
    
    Returns:
        Number of students in target cohort
    """
    if cohort_percentage is None:
        cohort_percentage = np.random.uniform(0.08, 0.10)
    
    cohort_size = int(total_students * cohort_percentage)
    return max(cohort_size, 1)  # Ensure at least 1


def calculate_saturation_with_rural_penalty(rural: bool, alpha: float = 5, beta: float = 2) -> float:
    """
    Generate saturation_rate using Beta distribution with rural penalty.
    
    Beta(α=5, β=2) produces high saturation rates (skewed towards 1.0)
    with realistic variance. Rural schools get 0.15 penalty factor.
    
    Args:
        rural: Whether school is in rural zone
        alpha: Beta distribution shape parameter α
        beta: Beta distribution shape parameter β
    
    Returns:
        Saturation rate (0-1), adjusted for rural access barriers
    """
    base_saturation = np.random.beta(alpha, beta)
    
    if rural:
        # Apply 0.15 penalty factor to rural schools
        base_saturation = base_saturation * (1 - 0.15)
    
    return np.clip(base_saturation, 0, 1)


def calculate_gender_parity(female_saturation: float, male_saturation: float) -> Tuple[float, bool]:
    """
    Calculate Gender Parity Index (GPI) as Female/Male saturation ratio.
    Flag equity_risk if GPI < 0.9 (indicating female underrepresentation).
    
    Args:
        female_saturation: Female enrollment saturation (0-1)
        male_saturation: Male enrollment saturation (0-1)
    
    Returns:
        Tuple of (gpi, equity_risk_flag)
    """
    if male_saturation == 0:
        gpi = female_saturation
    else:
        gpi = female_saturation / male_saturation
    
    equity_risk = gpi < 0.9
    
    return np.clip(gpi, 0, 2), equity_risk


def calculate_access_risk_score(lat: float, lon: float, max_distance_km: float = 50) -> Tuple[float, str]:
    """
    Calculate access_risk_score (0-100) as minimum distance to nearest center.
    Normalize: 0 km = 0 risk, max_distance_km = 100 risk.
    
    Schools with score > 75 are 'Dark Zones' (severely underserved).
    
    Args:
        lat, lon: School coordinates
        max_distance_km: Maximum distance threshold for 100% risk
    
    Returns:
        Tuple of (access_risk_score, zone_label)
    """
    distances = [
        haversine_distance(lat, lon, center["lat"], center["lon"])
        for center in ENROLLMENT_CENTERS
    ]
    
    min_distance = min(distances)
    
    # Normalize: 0 km = 0 risk, max_distance_km = 100 risk
    access_risk_score = min((min_distance / max_distance_km) * 100, 100)
    
    if access_risk_score > 75:
        zone_label = "Dark Zone"
    elif access_risk_score > 50:
        zone_label = "Moderate Access"
    else:
        zone_label = "Accessible"
    
    return access_risk_score, zone_label


def generate_school_id(index: int) -> str:
    """Generate unique school identifier."""
    return f"SCH-{10000 + index}"


# ==========================================
# 3. DIGITAL TWIN DATASET GENERATOR
# ==========================================

def generate_digital_twin_dataset(
    n_schools: int = 200,
    seed: int = 42,
    lat_range: Tuple[float, float] = (12.85, 13.35),
    lon_range: Tuple[float, float] = (77.35, 77.75)
) -> pd.DataFrame:
    """
    Generate a high-fidelity synthetic dataset simulating school-level 
    Aadhaar enrollment patterns with equity, access, and backlog metrics.
    
    This dataset simulates:
    - Invisible backlog (age-15 cohorts not yet enrolled)
    - Rural/urban disparities (penalty for rural access)
    - Gender parity issues (GPI < 0.9 flags equity risk)
    - Access barriers (distance-based dark zones)
    
    Args:
        n_schools: Number of schools to generate (default: 200)
        seed: Random seed for reproducibility
        lat_range: Latitude range (default: Karnataka region)
        lon_range: Longitude range (default: Karnataka region)
    
    Returns:
        pandas.DataFrame with columns:
            - school_id: Unique identifier
            - school_name: Human-readable name
            - latitude, longitude: GPS coordinates
            - category: 'rural' or 'urban'
            - total_students: Total enrollment
            - age_15_cohort: Target enrollment group size
            - female_students: Female enrollment
            - male_students: Male enrollment
            - saturation_rate: Overall enrollment coverage (0-1)
            - female_saturation: Female coverage (0-1)
            - male_saturation: Male coverage (0-1)
            - gender_parity_index: Female/Male saturation ratio
            - equity_risk: Boolean flag (GPI < 0.9)
            - backlog_students: Estimated unenrolled cohort
            - access_risk_score: Distance-based risk (0-100)
            - zone_label: 'Dark Zone', 'Moderate Access', 'Accessible'
            - priority_score: Composite urgency metric (0-1)
    """
    np.random.seed(seed)
    
    records = []
    
    for i in range(n_schools):
        # Basic school info
        school_id = generate_school_id(i)
        lat = np.random.uniform(lat_range[0], lat_range[1])
        lon = np.random.uniform(lon_range[0], lon_range[1])
        
        # Classification
        rural = is_rural(lat, lon)
        category = "rural" if rural else "urban"
        
        # School size
        total_students = np.random.randint(100, 800)
        
        # Age-15 cohort (target group)
        age_15_cohort = calculate_cohort_backlog(total_students)
        
        # Gender distribution (roughly 50/50, with some variance)
        female_ratio = np.random.uniform(0.45, 0.55)
        female_students = int(total_students * female_ratio)
        male_students = total_students - female_students
        
        # Saturation rates
        saturation_rate = calculate_saturation_with_rural_penalty(rural)
        female_saturation = calculate_saturation_with_rural_penalty(rural)
        male_saturation = calculate_saturation_with_rural_penalty(rural)
        
        # Gender Parity Index & Equity Risk
        gpi, equity_risk = calculate_gender_parity(female_saturation, male_saturation)
        
        # Backlog estimation
        backlog_students = max(0, age_15_cohort - int(age_15_cohort * saturation_rate))
        
        # Access Risk
        access_risk_score, zone_label = calculate_access_risk_score(lat, lon)
        
        # Priority Score: composite metric (higher = more urgent)
        # Factors: high backlog, equity risk, low saturation, high access risk
        backlog_weight = min(backlog_students / 100, 1.0)  # Normalize to 0-1
        access_weight = access_risk_score / 100
        saturation_weight = 1 - saturation_rate
        equity_weight = 1.0 if equity_risk else 0.0
        
        priority_score = (
            0.4 * backlog_weight +
            0.25 * access_weight +
            0.2 * saturation_weight +
            0.15 * equity_weight
        )
        
        # Generate school name
        blocks = ["Devanahalli", "Doddaballapur", "Hoskote", "Magadi", "Nelamangala", "Ramanagara"]
        school_types = ["Govt Primary School", "Govt High School", "Zilla Parishad School", "Model Govt School"]
        school_name = f"{np.random.choice(school_types)}, {np.random.choice(blocks)} Block-{np.random.randint(1, 10)}"
        
        record = {
            "school_id": school_id,
            "school_name": school_name,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "category": category,
            "total_students": total_students,
            "age_15_cohort": age_15_cohort,
            "female_students": female_students,
            "male_students": male_students,
            "saturation_rate": round(saturation_rate, 3),
            "female_saturation": round(female_saturation, 3),
            "male_saturation": round(male_saturation, 3),
            "gender_parity_index": round(gpi, 3),
            "equity_risk": equity_risk,
            "backlog_students": backlog_students,
            "access_risk_score": round(access_risk_score, 1),
            "zone_label": zone_label,
            "priority_score": round(priority_score, 3),
        }
        
        records.append(record)
    
    df = pd.DataFrame(records)
    
    # Add summary statistics
    df["status"] = df["backlog_students"].apply(
        lambda x: "CRITICAL" if x > df["backlog_students"].quantile(0.75) else "NORMAL"
    )
    
    return df


# ==========================================
# 4. ANALYSIS & VALIDATION FUNCTIONS
# ==========================================

def get_dataset_summary(df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics for the digital twin dataset.
    
    Args:
        df: Digital twin DataFrame
    
    Returns:
        Dictionary of key metrics
    """
    return {
        "total_schools": len(df),
        "rural_schools": len(df[df["category"] == "rural"]),
        "urban_schools": len(df[df["category"] == "urban"]),
        "dark_zones": len(df[df["zone_label"] == "Dark Zone"]),
        "equity_risk_schools": len(df[df["equity_risk"]]),
        "total_cohort": int(df["age_15_cohort"].sum()),
        "total_backlog": int(df["backlog_students"].sum()),
        "avg_saturation": round(df["saturation_rate"].mean(), 3),
        "avg_gpi": round(df["gender_parity_index"].mean(), 3),
        "avg_access_risk": round(df["access_risk_score"].mean(), 1),
    }


def identify_priority_clusters(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Identify top-priority schools for immediate intervention.
    
    Args:
        df: Digital twin DataFrame
        top_n: Number of schools to return
    
    Returns:
        DataFrame of top-priority schools sorted by priority_score
    """
    return df.nlargest(top_n, "priority_score")[
        ["school_id", "school_name", "category", "backlog_students", 
         "gender_parity_index", "equity_risk", "access_risk_score", "priority_score"]
    ]
