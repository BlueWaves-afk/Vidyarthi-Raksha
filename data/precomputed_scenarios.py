"""
Scenario Cache for Policy-Aware Routing
=======================================
Provides REAL route optimization using the CVRPTW algorithm from core/optimization.py.
Routes are computed on-demand for different policy modes (efficiency/balanced/equity).

This replaces the previous stub implementation with actual algorithmic routing.
"""

import pandas as pd
import numpy as np
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Import the REAL optimizer
from core.optimization import RouteOptimizer, haversine_distance


# ==========================================
# SCENARIO CONFIGURATION
# ==========================================

SCENARIO_CONFIG = {
    "efficiency": {
        "name": "Maximum Efficiency",
        "description": "Optimized for minimal travel distance and fuel consumption",
        "backlog_weight": 0.3,
        "access_weight": 0.7,
        "max_capacity": 180,  # Higher capacity utilization
        "color": "#3b82f6",
    },
    "balanced": {
        "name": "Balanced Approach", 
        "description": "Equal weight on backlog clearance and geographic access",
        "backlog_weight": 0.5,
        "access_weight": 0.5,
        "max_capacity": 150,
        "color": "#f59e0b",
    },
    "equity": {
        "name": "Equity Priority",
        "description": "Prioritizes underserved Dark Zones with high access barriers",
        "backlog_weight": 0.8,
        "access_weight": 0.2,
        "max_capacity": 120,  # Lower capacity to reach more remote areas
        "color": "#10b981",
    },
}

# Route colors for visualization
ROUTE_COLORS = [
    [234, 88, 12, 220],    # Orange - VAN-001
    [59, 130, 246, 220],   # Blue - VAN-002
    [16, 185, 129, 220],   # Green - VAN-003
    [147, 51, 234, 220],   # Purple - VAN-004
    [239, 68, 68, 220],    # Red - VAN-005
]


# ==========================================
# REAL ROUTE GENERATION (Using Optimizer)
# ==========================================

def generate_demo_routes(df: pd.DataFrame, num_vehicles: int = 3, 
                         scenario: str = "balanced") -> List[Dict]:
    """
    Generate routes using the REAL CVRPTW optimizer.
    
    Args:
        df: School dataframe with lat/lon, backlog, access_risk_score
        num_vehicles: Number of mobile enrollment units
        scenario: "efficiency", "equity", or "balanced"
    
    Returns:
        List of route dictionaries with path coordinates for visualization
    """
    config = SCENARIO_CONFIG.get(scenario, SCENARIO_CONFIG["balanced"])
    
    # Create optimizer with scenario-specific settings
    optimizer = RouteOptimizer(
        depot_lat=df['latitude'].mean(),  # Use centroid as depot
        depot_lon=df['longitude'].mean(),
        max_capacity=config["max_capacity"],
        max_time_minutes=480  # 8 hours
    )
    
    # Modify priority calculation based on scenario weights
    # We'll pre-process the data to adjust priority scoring
    schools_df = df.copy()
    
    # Apply scenario-specific weighting
    backlog_w = config["backlog_weight"]
    access_w = config["access_weight"]
    
    # Normalize and create weighted priority
    if 'backlog_students' in schools_df.columns and schools_df['backlog_students'].max() > 0:
        schools_df['norm_backlog'] = schools_df['backlog_students'] / schools_df['backlog_students'].max()
    else:
        schools_df['norm_backlog'] = 0
        
    if 'access_risk_score' in schools_df.columns:
        schools_df['norm_access'] = schools_df['access_risk_score'] / 100
    else:
        schools_df['norm_access'] = 0.5
    
    # Weighted priority - higher means more important
    schools_df['weighted_priority'] = (
        backlog_w * schools_df['norm_backlog'] + 
        access_w * schools_df['norm_access']
    )
    
    # Sort by weighted priority for clustering input
    schools_df = schools_df.sort_values('weighted_priority', ascending=False)
    
    # Run the REAL optimizer
    routes_data = optimizer.optimize_routes(schools_df, num_vehicles)
    
    # Convert to visualization format with paths for PyDeck
    viz_routes = []
    depot_lat, depot_lon = optimizer.depot_lat, optimizer.depot_lon
    
    for i, route in enumerate(routes_data):
        # Build path coordinates for PyDeck PathLayer (lon, lat format)
        path_coords = [[depot_lon, depot_lat]]  # Start at depot
        
        for school in route['schools']:
            path_coords.append([school['longitude'], school['latitude']])
        
        path_coords.append([depot_lon, depot_lat])  # Return to depot
        
        # Calculate efficiency score
        total_dist = route['total_distance_km']
        total_students = route['total_students']
        efficiency_score = min(100, int((total_students / max(total_dist, 1)) * 10))
        
        viz_route = {
            "vehicle_id": route['vehicle_id'],
            "path": path_coords,
            "color": ROUTE_COLORS[i % len(ROUTE_COLORS)],
            "total_students": route['total_students'],
            "total_distance_km": route['total_distance_km'],
            "total_time_minutes": route['total_time_minutes'],
            "num_schools": route['num_schools'],
            "schools": route['schools'],
            "efficiency_score": efficiency_score,
            "scenario": scenario,
        }
        
        viz_routes.append(viz_route)
    
    return viz_routes


# ==========================================
# MOBILE UNIT POSITIONS
# ==========================================

def generate_mobile_unit_positions(routes: List[Dict], progress: float = 0.3) -> List[Dict]:
    """
    Generate current positions of mobile units along their routes.
    
    Args:
        routes: List of route dictionaries with paths
        progress: Fraction of route completed (0-1)
    
    Returns:
        List of unit position dictionaries for visualization
    """
    units = []
    
    for route in routes:
        path = route.get('path', [])
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
            "efficiency_score": route.get('efficiency_score', 75),
            "color": route.get('color', [234, 88, 12, 220]),
        })
    
    return units


# ==========================================
# HEXAGON DATA FOR 3D MAP
# ==========================================

def get_hexagon_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare data for HexagonLayer visualization.
    
    Args:
        df: School dataframe
    
    Returns:
        DataFrame with columns for HexagonLayer
    """
    required_cols = ['latitude', 'longitude', 'backlog_students', 'access_risk_score', 'zone_label']
    available_cols = [c for c in required_cols if c in df.columns]
    
    hex_df = df[available_cols].copy()
    hex_df = hex_df.dropna(subset=['latitude', 'longitude'])
    
    # Compute elevation weight (for 3D height)
    if 'backlog_students' in hex_df.columns:
        max_backlog = hex_df['backlog_students'].max()
        if max_backlog > 0:
            hex_df['elevation_weight'] = hex_df['backlog_students'] / max_backlog * 100
        else:
            hex_df['elevation_weight'] = 0
    else:
        hex_df['elevation_weight'] = 50
    
    return hex_df


# ==========================================
# SCENARIO CACHE (Real Optimization)
# ==========================================

class ScenarioCache:
    """
    Cache for optimized route scenarios.
    Uses the REAL CVRPTW optimizer from core/optimization.py.
    """
    
    def __init__(self):
        self.routes: Dict[str, List[Dict]] = {}
        self.units: Dict[str, List[Dict]] = {}
        self._df: Optional[pd.DataFrame] = None
        self._num_vehicles: int = 3
    
    def precompute_all(self, df: pd.DataFrame, num_vehicles: int = 3):
        """
        Precompute all scenarios using the REAL optimizer.
        
        Args:
            df: School dataframe
            num_vehicles: Number of mobile units
        """
        self._df = df.copy()
        self._num_vehicles = num_vehicles
        
        for scenario in ["efficiency", "balanced", "equity"]:
            # Generate REAL routes using the optimizer
            routes = generate_demo_routes(df, num_vehicles, scenario)
            self.routes[scenario] = routes
            
            # Generate initial unit positions
            self.units[scenario] = generate_mobile_unit_positions(routes, 0.3)
    
    def get_routes(self, scenario: str) -> List[Dict]:
        """Get optimized routes for a scenario."""
        scenario = scenario.lower()
        
        # If not cached and we have data, compute on demand
        if scenario not in self.routes and self._df is not None:
            self.routes[scenario] = generate_demo_routes(
                self._df, self._num_vehicles, scenario
            )
        
        return self.routes.get(scenario, [])
    
    def get_units(self, scenario: str) -> List[Dict]:
        """Get mobile unit positions for a scenario."""
        scenario = scenario.lower()
        
        if scenario not in self.units:
            routes = self.get_routes(scenario)
            self.units[scenario] = generate_mobile_unit_positions(routes, 0.3)
        
        return self.units.get(scenario, [])
    
    def get_scenario_info(self, scenario: str) -> Dict:
        """Get scenario configuration metadata."""
        return SCENARIO_CONFIG.get(scenario.lower(), SCENARIO_CONFIG["balanced"])
    
    def clear(self):
        """Clear all cached data."""
        self.routes = {}
        self.units = {}
        self._df = None


# ==========================================
# SINGLETON CACHE INSTANCE
# ==========================================

_scenario_cache: Optional[ScenarioCache] = None

def get_scenario_cache() -> ScenarioCache:
    """Get or create the scenario cache singleton."""
    global _scenario_cache
    if _scenario_cache is None:
        _scenario_cache = ScenarioCache()
    return _scenario_cache
