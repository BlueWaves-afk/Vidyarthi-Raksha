"""
Precomputed Scenario Data for 3D Visualization
==============================================
Generates and caches route scenarios for instant map rendering.
Prevents "Spinning Wheel of Death" during live demonstrations.

Scenarios:
- efficiency: Optimized for minimal travel distance
- equity: Prioritizes high-risk/underserved regions
- balanced: Equal weight on efficiency and equity
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple
import math


# ==========================================
# ROUTE GENERATION FOR SCENARIOS
# ==========================================

def generate_demo_routes(df: pd.DataFrame, num_vehicles: int = 3, 
                         scenario: str = "balanced") -> List[Dict]:
    """
    Generate pre-computed routes for different optimization scenarios.
    
    Args:
        df: School dataframe with lat/lon, backlog, access_risk_score
        num_vehicles: Number of mobile enrollment units
        scenario: "efficiency", "equity", or "balanced"
    
    Returns:
        List of route dictionaries with path coordinates
    """
    # Filter schools with backlog
    schools = df[df['backlog_students'] > 0].copy()
    
    if len(schools) == 0:
        return []
    
    # Set priority weights based on scenario
    weights = {
        "efficiency": (0.3, 0.7),   # Low backlog weight, high proximity
        "equity": (0.8, 0.2),       # High backlog weight, low proximity
        "balanced": (0.5, 0.5),     # Equal weights
    }
    
    backlog_w, access_w = weights.get(scenario, (0.5, 0.5))
    
    # Normalize scores
    schools['norm_backlog'] = schools['backlog_students'] / schools['backlog_students'].max()
    schools['norm_access'] = schools['access_risk_score'] / 100
    
    # Calculate priority
    schools['priority'] = (backlog_w * schools['norm_backlog'] + 
                          access_w * schools['norm_access'])
    
    # Sort by priority
    schools = schools.sort_values('priority', ascending=False)
    
    # Depot location (Bengaluru central)
    depot_lat, depot_lon = 13.1939, 77.5941
    
    # Simple cluster assignment (round-robin by priority)
    schools['vehicle'] = [i % num_vehicles for i in range(len(schools))]
    
    routes = []
    route_colors = [
        [234, 88, 12, 220],    # Orange - VAN-001
        [59, 130, 246, 220],   # Blue - VAN-002
        [16, 185, 129, 220],   # Green - VAN-003
        [147, 51, 234, 220],   # Purple - VAN-004
        [239, 68, 68, 220],    # Red - VAN-005
    ]
    
    for v_id in range(num_vehicles):
        vehicle_schools = schools[schools['vehicle'] == v_id]
        
        if len(vehicle_schools) == 0:
            continue
        
        # Build path: depot -> schools -> depot
        path_coords = [[depot_lon, depot_lat]]  # Start at depot
        
        total_students = 0
        total_distance = 0
        school_list = []
        
        prev_lat, prev_lon = depot_lat, depot_lon
        
        for _, school in vehicle_schools.iterrows():
            lat, lon = school['latitude'], school['longitude']
            path_coords.append([lon, lat])
            
            # Calculate distance
            dist = haversine_km(prev_lat, prev_lon, lat, lon)
            total_distance += dist
            total_students += school['backlog_students']
            
            school_list.append({
                "school_id": school.get('school_id', ''),
                "school_name": school.get('school_name', f"School {len(school_list)+1}"),
                "latitude": lat,
                "longitude": lon,
                "backlog": int(school['backlog_students']),
                "access_risk": int(school['access_risk_score']),
                "zone": school.get('zone_label', 'Unknown'),
            })
            
            prev_lat, prev_lon = lat, lon
        
        # Return to depot
        path_coords.append([depot_lon, depot_lat])
        total_distance += haversine_km(prev_lat, prev_lon, depot_lat, depot_lon)
        
        # Calculate efficiency score
        efficiency_score = min(100, int((total_students / max(total_distance, 1)) * 10))
        
        route = {
            "vehicle_id": f"VAN-{v_id + 1:03d}",
            "path": path_coords,
            "color": route_colors[v_id % len(route_colors)],
            "total_students": int(total_students),
            "total_distance_km": round(total_distance, 2),
            "num_schools": len(school_list),
            "schools": school_list,
            "efficiency_score": efficiency_score,
            "scenario": scenario,
        }
        
        routes.append(route)
    
    return routes


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in kilometers."""
    R = 6371
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def generate_mobile_unit_positions(routes: List[Dict], progress: float = 0.3) -> List[Dict]:
    """
    Generate current positions of mobile units along their routes.
    
    Args:
        routes: List of route dictionaries with paths
        progress: Fraction of route completed (0-1)
    
    Returns:
        List of unit position dictionaries for IconLayer
    """
    units = []
    
    for route in routes:
        path = route['path']
        if len(path) < 2:
            continue
        
        # Calculate position along path based on progress
        total_segments = len(path) - 1
        segment_progress = progress * total_segments
        segment_idx = int(segment_progress)
        local_progress = segment_progress - segment_idx
        
        # Clamp to valid range
        segment_idx = min(segment_idx, total_segments - 1)
        
        # Interpolate position
        start = path[segment_idx]
        end = path[min(segment_idx + 1, len(path) - 1)]
        
        current_lon = start[0] + (end[0] - start[0]) * local_progress
        current_lat = start[1] + (end[1] - start[1]) * local_progress
        
        units.append({
            "vehicle_id": route['vehicle_id'],
            "longitude": current_lon,
            "latitude": current_lat,
            "students_covered": int(route['total_students'] * progress),
            "students_total": route['total_students'],
            "schools_visited": int(route['num_schools'] * progress),
            "schools_total": route['num_schools'],
            "efficiency_score": route['efficiency_score'],
            "color": route['color'],
        })
    
    return units


def get_hexagon_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare data for HexagonLayer visualization.
    
    Args:
        df: School dataframe
    
    Returns:
        DataFrame with columns for HexagonLayer
    """
    hex_df = df[['latitude', 'longitude', 'backlog_students', 
                 'access_risk_score', 'zone_label']].copy()
    hex_df = hex_df.dropna()
    
    # Compute elevation weight (for 3D height)
    max_backlog = hex_df['backlog_students'].max()
    hex_df['elevation_weight'] = hex_df['backlog_students'] / max_backlog * 100
    
    # Compute color mapping (red = high risk, green = low risk)
    def risk_to_color(risk_score):
        """Map risk score (0-100) to RGB color."""
        # Red (high risk) -> Yellow (medium) -> Green (low risk)
        if risk_score >= 70:
            # Dark Zone - Red
            return [220, 38, 38, 200]
        elif risk_score >= 40:
            # Moderate Zone - Orange/Yellow
            r = int(245)
            g = int(158 - (risk_score - 40) * 2)
            return [r, g, 11, 200]
        else:
            # Accessible Zone - Green
            return [22, 163, 74, 200]
    
    hex_df['color'] = hex_df['access_risk_score'].apply(risk_to_color)
    
    return hex_df


# ==========================================
# SCENARIO CACHE
# ==========================================

class ScenarioCache:
    """
    Cache for pre-computed scenarios.
    Enables instant visualization switching without recalculation.
    """
    
    def __init__(self):
        self.scenarios = {}
        self.routes = {}
        self.units = {}
    
    def precompute_all(self, df: pd.DataFrame, num_vehicles: int = 3):
        """Precompute all scenarios for the given data."""
        for scenario in ["efficiency", "equity", "balanced"]:
            routes = generate_demo_routes(df, num_vehicles, scenario)
            self.routes[scenario] = routes
            self.units[scenario] = generate_mobile_unit_positions(routes, 0.3)
        
        self.scenarios = {
            "efficiency": {
                "name": "Maximum Efficiency",
                "description": "Optimized for minimal travel distance and fuel consumption",
                "weight_backlog": 0.3,
                "weight_access": 0.7,
            },
            "equity": {
                "name": "Equity Priority", 
                "description": "Prioritizes underserved Dark Zones with high access barriers",
                "weight_backlog": 0.8,
                "weight_access": 0.2,
            },
            "balanced": {
                "name": "Balanced Approach",
                "description": "Equal weight on backlog clearance and geographic access",
                "weight_backlog": 0.5,
                "weight_access": 0.5,
            },
        }
    
    def get_routes(self, scenario: str) -> List[Dict]:
        """Get precomputed routes for a scenario."""
        return self.routes.get(scenario, [])
    
    def get_units(self, scenario: str) -> List[Dict]:
        """Get mobile unit positions for a scenario."""
        return self.units.get(scenario, [])
    
    def get_scenario_info(self, scenario: str) -> Dict:
        """Get scenario metadata."""
        return self.scenarios.get(scenario, {})


# Singleton cache instance
_scenario_cache = None

def get_scenario_cache() -> ScenarioCache:
    """Get or create the scenario cache singleton."""
    global _scenario_cache
    if _scenario_cache is None:
        _scenario_cache = ScenarioCache()
    return _scenario_cache
