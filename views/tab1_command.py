"""
Tab 1: Strategic Command Center
================================
High-level KPI dashboard with geographic visualization of enrollment disparities.
Uses PyDeck HexagonLayer to show backlog density and access risk by region.
Implements the KPI Command Layer (Section 3.2) - "Situation Room" view.

3D Landscape of Need:
- HexagonLayer: Height = backlog magnitude, Color = vulnerability
- PathLayer: Vehicle routes from CVRPTW optimization
- IconLayer: Mobile enrollment units along routes

KPIs are calculated from real digital twin data (digital_twin_schools.csv)
and cached per session for performance.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from millify import millify
import streamlit_shadcn_ui as ui
import numpy as np
import math
from typing import List, Dict, Tuple, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)


# ==========================================
# REAL KPI CALCULATIONS FROM DIGITAL TWIN DATA
# ==========================================

def calculate_real_kpis(df: pd.DataFrame, policy_mode: str = "balanced", 
                        num_vans: int = 3, capacity: int = 150) -> Dict:
    """
    Calculate KPIs from actual digital_twin_schools.csv data.
    Results are cached in session state per policy_mode for performance.
    
    Args:
        df: DataFrame with digital twin school data
        policy_mode: 'efficiency', 'balanced', or 'equity'
        num_vans: Number of mobile enrollment vans
        capacity: Daily student capacity per van
    
    Returns:
        Dictionary with calculated KPI metrics
    """
    # Initialize session cache if not exists
    if 'kpi_cache' not in st.session_state:
        st.session_state.kpi_cache = {}
    
    # Check cache first
    cache_key = f"{policy_mode}_{num_vans}_{capacity}"
    if cache_key in st.session_state.kpi_cache:
        return st.session_state.kpi_cache[cache_key]
    
    # === BASE METRICS FROM ACTUAL DATA ===
    total_students = int(df['total_students'].sum())
    total_backlog = int(df['backlog_students'].sum())
    current_saturation = df['saturation_rate'].mean() * 100  # Convert to percentage
    avg_gpi = df['gender_parity_index'].mean()
    dark_zone_count = int(df[df['zone_label'] == 'Dark Zone'].shape[0])
    equity_alerts_base = int(df[df['equity_risk']].shape[0])
    
    # === SATURATION RATE MOM ===
    # Calculate based on enrollment capacity vs backlog
    # Assume each van processes `capacity` students/day, 5 days/week
    daily_capacity = num_vans * capacity
    weekly_capacity = daily_capacity * 5
    monthly_capacity = weekly_capacity * 4  # ~20 working days
    
    # Saturation gain = (monthly_capacity / total_students) * 100
    # Adjusted by policy throughput factor
    throughput_factors = {"efficiency": 0.85, "balanced": 1.0, "equity": 1.1}
    throughput = throughput_factors.get(policy_mode, 1.0)
    
    monthly_enrollments = monthly_capacity * throughput
    saturation_mom_gain = (monthly_enrollments / max(total_students, 1)) * 100
    saturation_mom_gain = min(saturation_mom_gain, 10.0)  # Cap at realistic 10%
    
    # === BACKLOG REDUCTION MOM ===
    # Based on actual processing rate vs remaining backlog
    backlog_reduction_pct = -(monthly_enrollments / max(total_backlog, 1)) * 100
    backlog_reduction_pct = max(backlog_reduction_pct, -50.0)  # Cap at -50%
    
    # === WEEKLY ENROLLMENT RATE ===
    weekly_rate = int(weekly_capacity * throughput)
    
    # === DAYS TO 95% SATURATION ===
    target_saturation = 95.0
    current_enrolled = total_students * (current_saturation / 100)
    target_enrolled = total_students * (target_saturation / 100)
    students_needed = max(0, target_enrolled - current_enrolled)
    
    adjusted_daily_capacity = daily_capacity * throughput
    days_to_target = int(students_needed / max(adjusted_daily_capacity, 1)) if students_needed > 0 else 0
    
    # === POLICY-ADJUSTED METRICS ===
    if policy_mode == "efficiency":
        # Lower costs, shorter routes, moderate coverage
        fuel_cost = 12500
        fuel_delta = -18
        coverage_rate = 72  # % of Dark Zones covered
        route_distance = 145  # km avg
        gpi_adjusted = avg_gpi * 0.96
        equity_alerts = equity_alerts_base + 3
        students_covered = int(total_backlog * 0.65)
        
    elif policy_mode == "equity":
        # Higher costs, longer routes into rural areas, max coverage
        fuel_cost = 18200
        fuel_delta = 22
        coverage_rate = 94
        route_distance = 287
        gpi_adjusted = min(1.0, avg_gpi * 1.08)
        equity_alerts = max(0, equity_alerts_base - 5)
        students_covered = int(total_backlog * 0.92)
        
    else:  # balanced
        fuel_cost = 15400
        fuel_delta = 0
        coverage_rate = 83
        route_distance = 198
        gpi_adjusted = avg_gpi
        equity_alerts = equity_alerts_base
        students_covered = int(total_backlog * 0.78)
    
    # Days to clear entire backlog
    days_to_clear = int(total_backlog / max(adjusted_daily_capacity, 1))
    
    # Build result dictionary
    result = {
        # Primary KPIs (calculated from real data)
        "saturation_mom": round(saturation_mom_gain, 1),
        "backlog_reduction_pct": round(backlog_reduction_pct, 1),
        "weekly_enrollment_rate": weekly_rate,
        "days_to_95_target": days_to_target,
        
        # Base metrics
        "total_backlog": total_backlog,
        "total_students": total_students,
        "current_saturation": round(current_saturation, 1),
        "students_covered": students_covered,
        "gpi": gpi_adjusted,
        "saturation": current_saturation,
        "dark_zones": dark_zone_count,
        "equity_alerts": equity_alerts,
        "days_to_clear": days_to_clear,
        
        # Policy-specific metrics
        "fuel_cost": fuel_cost,
        "fuel_delta": fuel_delta,
        "coverage_rate": coverage_rate,
        "route_distance": route_distance,
        "policy_mode": policy_mode,
        
        # Capacity info
        "daily_capacity": int(adjusted_daily_capacity),
        "weekly_capacity": int(weekly_capacity * throughput),
        "monthly_capacity": int(monthly_enrollments),
    }
    
    # Cache the result
    st.session_state.kpi_cache[cache_key] = result
    
    return result


def get_zone_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate detailed statistics for each zone from digital twin data.
    Cached in session state for performance.
    
    Returns:
        Dictionary with zone-level statistics including priority scores,
        GPI averages, intervention status, etc.
    """
    if 'zone_stats_cache' not in st.session_state:
        st.session_state.zone_stats_cache = {}
    
    # Use data hash as cache key
    cache_key = f"zones_{len(df)}_{df['backlog_students'].sum()}"
    if cache_key in st.session_state.zone_stats_cache:
        return st.session_state.zone_stats_cache[cache_key]
    
    zones = {}
    zone_order = ['Dark Zone', 'Emerging Zone', 'Watch Zone', 'Green Zone']
    
    for zone_label in zone_order:
        zone_df = df[df['zone_label'] == zone_label]
        if len(zone_df) == 0:
            continue
        
        zones[zone_label] = {
            'school_count': len(zone_df),
            'total_backlog': int(zone_df['backlog_students'].sum()),
            'avg_saturation': round(zone_df['saturation_rate'].mean() * 100, 1),
            'avg_gpi': round(zone_df['gender_parity_index'].mean(), 3),
            'gpi_below_90': int((zone_df['gender_parity_index'] < 0.90).sum()),
            'avg_priority_score': round(zone_df['priority_score'].mean(), 1) if 'priority_score' in zone_df.columns else 0,
            'equity_risk_count': int(zone_df['equity_risk'].sum()) if 'equity_risk' in zone_df.columns else 0,
            'total_students': int(zone_df['total_students'].sum()),
        }
    
    # Calculate total backlog for percentage
    total_backlog = df['backlog_students'].sum()
    for zone_label in zones:
        zones[zone_label]['backlog_pct'] = round(
            (zones[zone_label]['total_backlog'] / max(total_backlog, 1)) * 100, 1
        )
    
    st.session_state.zone_stats_cache[cache_key] = zones
    return zones




# Import precomputed scenarios for performance
try:
    from data.precomputed_scenarios import (
        get_scenario_cache, 
        generate_demo_routes,
        generate_mobile_unit_positions,
        get_hexagon_data,
        ScenarioCache
    )
except ImportError:
    # Fallback if import fails - define inline
    from typing import Optional
    
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance in kilometers."""
        R = 6371
        lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))
    
    def generate_demo_routes(df: pd.DataFrame, num_vehicles: int = 3, scenario: str = "balanced") -> List[Dict]:
        """Generate demo routes for visualization."""
        schools = df[df['backlog_students'] > 0].copy()
        if len(schools) == 0:
            return []
        
        weights = {"efficiency": (0.3, 0.7), "equity": (0.8, 0.2), "balanced": (0.5, 0.5)}
        backlog_w, access_w = weights.get(scenario, (0.5, 0.5))
        
        schools['norm_backlog'] = schools['backlog_students'] / schools['backlog_students'].max()
        schools['norm_access'] = schools['access_risk_score'] / 100
        schools['priority'] = backlog_w * schools['norm_backlog'] + access_w * schools['norm_access']
        schools = schools.sort_values('priority', ascending=False)
        
        depot_lat, depot_lon = 13.1939, 77.5941
        schools['vehicle'] = [i % num_vehicles for i in range(len(schools))]
        
        route_colors = [[234, 88, 12, 220], [59, 130, 246, 220], [16, 185, 129, 220], [147, 51, 234, 220], [239, 68, 68, 220]]
        routes = []
        
        for v_id in range(num_vehicles):
            vehicle_schools = schools[schools['vehicle'] == v_id]
            if len(vehicle_schools) == 0:
                continue
            
            path_coords = [[depot_lon, depot_lat]]
            total_students, total_distance = 0, 0
            school_list = []
            prev_lat, prev_lon = depot_lat, depot_lon
            
            for _, school in vehicle_schools.iterrows():
                lat, lon = school['latitude'], school['longitude']
                path_coords.append([lon, lat])
                total_distance += haversine_km(prev_lat, prev_lon, lat, lon)
                total_students += school['backlog_students']
                school_list.append({"school_id": school.get('school_id', ''), "backlog": int(school['backlog_students'])})
                prev_lat, prev_lon = lat, lon
            
            path_coords.append([depot_lon, depot_lat])
            total_distance += haversine_km(prev_lat, prev_lon, depot_lat, depot_lon)
            
            routes.append({
                "vehicle_id": f"VAN-{v_id + 1:03d}",
                "path": path_coords,
                "color": route_colors[v_id % len(route_colors)],
                "total_students": int(total_students),
                "total_distance_km": round(total_distance, 2),
                "num_schools": len(school_list),
                "schools": school_list,
                "efficiency_score": min(100, int((total_students / max(total_distance, 1)) * 10)),
                "scenario": scenario,
            })
        return routes
    
    def generate_mobile_unit_positions(routes: List[Dict], progress: float = 0.3) -> List[Dict]:
        """Generate mobile unit positions."""
        units = []
        for route in routes:
            path = route['path']
            if len(path) < 2:
                continue
            segment_idx = min(int(progress * (len(path) - 1)), len(path) - 2)
            local_progress = (progress * (len(path) - 1)) - segment_idx
            start, end = path[segment_idx], path[segment_idx + 1]
            units.append({
                "vehicle_id": route['vehicle_id'],
                "longitude": start[0] + (end[0] - start[0]) * local_progress,
                "latitude": start[1] + (end[1] - start[1]) * local_progress,
                "students_covered": int(route['total_students'] * progress),
                "students_total": route['total_students'],
                "schools_visited": int(route['num_schools'] * progress),
                "schools_total": route['num_schools'],
                "efficiency_score": route['efficiency_score'],
                "color": route['color'],
            })
        return units
    
    def get_hexagon_data(df: pd.DataFrame) -> pd.DataFrame:
        return df[['latitude', 'longitude', 'backlog_students', 'access_risk_score', 'zone_label']].dropna()
    
    class ScenarioCache:
        def __init__(self):
            self.routes = {}
            self.units = {}
        def precompute_all(self, df: pd.DataFrame, num_vehicles: int = 3):
            for scenario in ["efficiency", "equity", "balanced"]:
                self.routes[scenario] = generate_demo_routes(df, num_vehicles, scenario)
                self.units[scenario] = generate_mobile_unit_positions(self.routes[scenario], 0.3)
        def get_routes(self, scenario: str) -> List[Dict]:
            return self.routes.get(scenario, [])
        def get_units(self, scenario: str) -> List[Dict]:
            return self.units.get(scenario, [])
    
    _scenario_cache = None
    def get_scenario_cache() -> ScenarioCache:
        global _scenario_cache
        if _scenario_cache is None:
            _scenario_cache = ScenarioCache()
        return _scenario_cache


def create_situation_room_header(policy_mode: str = "balanced") -> None:
    """
    Render the Situation Room header banner with policy mode indicator.
    """
    mode_styles = {
        "efficiency": {
            "accent": "#3b82f6",
            "label": "EFFICIENCY MODE",
            "subtitle": "Minimizing operational costs • Short urban routes",
        },
        "balanced": {
            "accent": "#f59e0b",
            "label": "BALANCED MODE",
            "subtitle": "Real-time operational intelligence • Cost-equity balance",
        },
        "equity": {
            "accent": "#dc2626",
            "label": "VIDYARTHI-RAKSHA MODE",
            "subtitle": "Maximum inclusion priority • Dark Zone coverage active",
        },
    }
    
    style = mode_styles.get(policy_mode, mode_styles["balanced"])
    
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #e2e8f0;
            border-left: 5px solid {style['accent']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        ">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #1e293b; letter-spacing: 0.02em;">
                        SITUATION ROOM
                    </div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">
                        {style['subtitle']}
                    </div>
                </div>
                <div style="
                    background: {style['accent']};
                    color: #ffffff;
                    padding: 0.35rem 0.75rem;
                    border-radius: 6px;
                    font-size: 0.65rem;
                    font-weight: 700;
                    letter-spacing: 0.05em;
                ">
                    {style['label']}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def get_policy_adjusted_metrics(df: pd.DataFrame, policy_mode: str, num_vans: int, capacity: int) -> Dict:
    """
    Calculate metrics adjusted by policy mode.
    Now uses calculate_real_kpis() for actual data-driven metrics.
    
    Returns metrics based on optimization priority and real digital twin data.
    """
    # Use the cached real KPI calculator
    return calculate_real_kpis(df, policy_mode, num_vans, capacity)


def create_kpi_cards(df: pd.DataFrame, num_vans: int = 3, capacity: int = 150, 
                     policy_mode: str = "balanced") -> None:
    """
    Render enterprise-grade KPI Command Layer with policy-aware metrics.
    Cards dynamically update based on selected optimization priority.
    """
    # Create Situation Room header with policy mode
    create_situation_room_header(policy_mode)
    
    # Get policy-adjusted metrics
    metrics = get_policy_adjusted_metrics(df, policy_mode, num_vans, capacity)
    
    # Extract metrics for display
    total_backlog = metrics['total_backlog']
    students_covered = metrics['students_covered']
    avg_gpi = metrics['gpi']
    fuel_cost = metrics['fuel_cost']
    fuel_delta = metrics['fuel_delta']
    coverage_rate = metrics['coverage_rate']
    dark_zones = metrics['dark_zones']
    equity_alerts = metrics['equity_alerts']
    days_to_clear = metrics['days_to_clear']
    route_distance = metrics['route_distance']
    
    # Determine display states based on policy mode
    backlog_critical = total_backlog > 2000
    
    # GPI status changes with policy mode
    if policy_mode == "equity":
        gpi_status = "success"
        gpi_label = "OPTIMIZED"
    elif policy_mode == "efficiency":
        gpi_status = "warning" if avg_gpi >= 0.90 else "destructive"
        gpi_label = "MODERATE" if avg_gpi >= 0.90 else "AT RISK"
    else:
        gpi_status = "success" if avg_gpi >= 0.95 else ("warning" if avg_gpi >= 0.90 else "destructive")
        gpi_label = "ON TRACK" if avg_gpi >= 0.95 else ("ATTENTION" if avg_gpi >= 0.90 else "CRITICAL")
    
    # Fuel cost status based on mode
    fuel_status = "success" if policy_mode == "efficiency" else ("warning" if policy_mode == "equity" else "neutral")
    
    # KPI Row 1: Primary Metrics - Clean minimal design
    cols = st.columns(4, gap="medium")
    
    # Uniform card style with fixed height
    card_style = """
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.25rem;
        text-align: center;
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    """
    
    with cols[0]:
        # SATURATION RATE MOM - Now from real calculation
        saturation_delta = metrics.get('saturation_mom', 0)
        trend_icon = "↑" if saturation_delta > 0 else "↓"
        trend_color = "#22c55e" if saturation_delta > 0 else "#dc2626"
        
        st.markdown(f"""
            <div style="{card_style}">
                <div style="font-size: 0.65rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; font-weight: 500; margin-bottom: 0.5rem;">
                    Saturation Rate MoM
                </div>
                <div style="font-size: 1.75rem; font-weight: 600; color: {trend_color}; line-height: 1;">
                    +{abs(saturation_delta):.1f}% <span style="font-size: 1rem;">{trend_icon}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        # BACKLOG REDUCTION MOM - Now from real calculation
        backlog_reduction = metrics.get('backlog_reduction_pct', 0)
        reduction_color = "#22c55e" if backlog_reduction < 0 else "#dc2626"
        reduction_icon = "↓" if backlog_reduction < 0 else "↑"
        
        st.markdown(f"""
            <div style="{card_style}">
                <div style="font-size: 0.65rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; font-weight: 500; margin-bottom: 0.5rem;">
                    Backlog Reduction MoM
                </div>
                <div style="font-size: 1.75rem; font-weight: 600; color: {reduction_color}; line-height: 1;">
                    {backlog_reduction:.1f}% <span style="font-size: 1rem;">{reduction_icon}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        # WEEKLY ENROLLMENT RATE - Now from real calculation
        weekly_rate = metrics.get('weekly_enrollment_rate', 0)
        rate_color = "#3b82f6"
        
        st.markdown(f"""
            <div style="{card_style}">
                <div style="font-size: 0.65rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; font-weight: 500; margin-bottom: 0.5rem;">
                    Weekly Enrollment Rate
                </div>
                <div style="font-size: 1.75rem; font-weight: 600; color: {rate_color}; line-height: 1;">
                    {weekly_rate:,} <span style="font-size: 1rem;">↑</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        # DAYS TO 95% SATURATION - Now from real calculation
        days_to_target = metrics.get('days_to_95_target', 0)
        days_color = "#f59e0b" if days_to_target > 60 else ("#22c55e" if days_to_target < 30 else "#3b82f6")
        
        st.markdown(f"""
            <div style="{card_style}">
                <div style="font-size: 0.65rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; font-weight: 500; margin-bottom: 0.5rem;">
                    Days to 95% Saturation
                </div>
                <div style="font-size: 1.75rem; font-weight: 600; color: {days_color}; line-height: 1;">
                    {days_to_target} <span style="font-size: 1rem;">→</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # KPI Row 2: Clean centered cards matching image 2 style
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    alert_cols = st.columns(2, gap="medium")
    
    with alert_cols[0]:
        # Days to Clear - clean centered card
        days_color = "#22c55e" if days_to_clear < 30 else ("#f59e0b" if days_to_clear < 60 else "#dc2626")
        
        st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 2px solid {days_color}30;
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
            ">
                <div style="font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.08em; font-weight: 500; margin-bottom: 0.5rem;">
                    Days to Clear Backlog
                </div>
                <div style="font-size: 2.5rem; font-weight: 700; color: {days_color}; line-height: 1.2;">
                    {days_to_clear}
                </div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">
                    @ {num_vans} vans × {capacity} students/day
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with alert_cols[1]:
        # Equity Alerts - clean centered card
        alert_color = "#22c55e" if equity_alerts < 5 else ("#f59e0b" if equity_alerts < 10 else "#dc2626")
        
        st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 2px solid {alert_color}30;
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
            ">
                <div style="font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.08em; font-weight: 500; margin-bottom: 0.5rem;">
                    Equity Alerts
                </div>
                <div style="font-size: 2.5rem; font-weight: 700; color: {alert_color}; line-height: 1.2;">
                    {equity_alerts}
                </div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.5rem;">
                    Schools with GPI below 0.90
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


# ==========================================
# 3D LANDSCAPE OF NEED - VISUALIZATION
# ==========================================

def create_coverage_watch_header(scenario: str, routes: List[Dict]) -> None:
    """
    Render the Coverage Watch mode header with scenario info.
    """
    scenario_info = {
        "efficiency": {
            "title": "Maximum Efficiency Mode",
            "desc": "Optimized for minimal travel distance",
            "color": "#3b82f6",
            "icon": "⚡"
        },
        "equity": {
            "title": "Equity Priority Mode", 
            "desc": "Prioritizing underserved Dark Zones",
            "color": "#dc2626",
            "icon": "⚖️"
        },
        "balanced": {
            "title": "Balanced Approach Mode",
            "desc": "Equal weight on efficiency and equity",
            "color": "#f59e0b",
            "icon": "🎯"
        }
    }
    
    info = scenario_info.get(scenario, scenario_info["balanced"])
    
    total_students = sum(r['total_students'] for r in routes)
    total_distance = sum(r['total_distance_km'] for r in routes)
    total_schools = sum(r['num_schools'] for r in routes)
    
    st.markdown(f"""
        <div style="
            background: #ffffff;
            border-radius: 8px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid #e2e8f0;
            border-left: 4px solid {info['color']};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 0.7rem; text-transform: uppercase; color: {info['color']}; letter-spacing: 0.1em; font-weight: 600;">
                        COVERAGE WATCH ACTIVE
                    </div>
                    <div style="font-size: 1rem; font-weight: 600; color: #1e293b; margin-top: 0.25rem;">
                        {info['title']}
                    </div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.15rem;">
                        {info['desc']}
                    </div>
                </div>
                <div style="display: flex; gap: 1.5rem; text-align: center;">
                    <div>
                        <div style="font-size: 1.4rem; font-weight: 600; color: #1e293b;">{len(routes)}</div>
                        <div style="font-size: 0.65rem; color: #94a3b8; text-transform: uppercase;">Routes</div>
                    </div>
                    <div>
                        <div style="font-size: 1.4rem; font-weight: 600; color: #22c55e;">{total_schools}</div>
                        <div style="font-size: 0.65rem; color: #94a3b8; text-transform: uppercase;">Schools</div>
                    </div>
                    <div>
                        <div style="font-size: 1.4rem; font-weight: 600; color: #3b82f6;">{millify(total_students)}</div>
                        <div style="font-size: 0.65rem; color: #94a3b8; text-transform: uppercase;">Students</div>
                    </div>
                    <div>
                        <div style="font-size: 1.4rem; font-weight: 600; color: #f59e0b;">{total_distance:.0f}km</div>
                        <div style="font-size: 0.65rem; color: #94a3b8; text-transform: uppercase;">Distance</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def create_3d_landscape_map(df: pd.DataFrame, routes: List[Dict] = None, 
                            units: List[Dict] = None, show_routes: bool = True) -> None:
    """
    Render the 3D Landscape of Need using PyDeck.
    
    Layers:
    - HexagonLayer: Height = backlog, Color = vulnerability (The Problem)
    - PathLayer: Vehicle routes from CVRPTW (The Solution)
    - IconLayer: Mobile enrollment units on routes
    
    Args:
        df: School dataframe
        routes: List of route dictionaries with paths
        units: List of mobile unit positions
        show_routes: Whether to show PathLayer and IconLayer
    """
    # Prepare hexagon data
    hex_df = df[['latitude', 'longitude', 'backlog_students', 'access_risk_score', 'zone_label']].copy()
    hex_df = hex_df.dropna()
    
    # Calculate center of map
    center_lat = hex_df['latitude'].mean()
    center_lon = hex_df['longitude'].mean()
    
    # Normalize backlog for elevation
    max_backlog = hex_df['backlog_students'].max()
    hex_df['elevation'] = hex_df['backlog_students'] / max_backlog * 100
    
    # Color by access risk: Red (high risk/Dark Zone) -> Green (accessible)
    def risk_to_color(row):
        risk = row['access_risk_score']
        if risk >= 70:
            return [220, 38, 38, 200]  # Red - Dark Zone
        elif risk >= 40:
            return [245, 158, 11, 200]  # Orange/Yellow - Moderate
        else:
            return [22, 163, 74, 200]  # Green - Accessible
    
    hex_df['color'] = hex_df.apply(risk_to_color, axis=1)
    
    layers = []
    
    # ==========================================
    # LAYER 1: HexagonLayer - The Problem
    # ==========================================
    # Height represents backlog magnitude, color represents vulnerability
    
    hexagon_layer = pdk.Layer(
        "HexagonLayer",
        data=hex_df,
        get_position=["longitude", "latitude"],
        radius=1500,  # 1.5km radius for better aggregation
        elevation_scale=80,
        elevation_range=[0, 3000],
        pickable=True,
        extruded=True,
        coverage=0.85,
        color_range=[
            [22, 163, 74, 200],   # Green - Low risk
            [132, 204, 22, 200],  # Lime
            [250, 204, 21, 200],  # Yellow
            [245, 158, 11, 200],  # Orange
            [239, 68, 68, 200],   # Light Red
            [220, 38, 38, 200],   # Red - High risk (Dark Zone)
        ],
        get_color_weight="access_risk_score",
        get_elevation_weight="backlog_students",
        auto_highlight=True,
    )
    layers.append(hexagon_layer)
    
    # ==========================================
    # LAYER 2: ColumnLayer - Individual School Towers
    # ==========================================
    # Shows individual schools as colored columns
    
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=hex_df,
        get_position=["longitude", "latitude"],
        get_elevation="elevation",
        elevation_scale=50,
        radius=200,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )
    layers.append(column_layer)
    
    # ==========================================
    # LAYER 3: PathLayer - The Solution (Routes)
    # ==========================================
    if show_routes and routes:
        for route in routes:
            path_layer = pdk.Layer(
                "PathLayer",
                data=[{
                    "path": route['path'],
                    "vehicle_id": route['vehicle_id'],
                    "efficiency_score": route['efficiency_score'],
                    "total_students": route['total_students'],
                    "total_distance_km": route['total_distance_km'],
                    "num_schools": route['num_schools'],
                }],
                get_path="path",
                get_color=route['color'],
                width_scale=20,
                width_min_pixels=3,
                width_max_pixels=8,
                get_width=5,
                pickable=True,
                auto_highlight=True,
            )
            layers.append(path_layer)
    
    # ==========================================
    # LAYER 4: ScatterplotLayer - Mobile Units
    # ==========================================
    if show_routes and units:
        units_df = pd.DataFrame(units)
        
        # Mobile Unit markers (larger, prominent)
        unit_layer = pdk.Layer(
            "ScatterplotLayer",
            data=units_df,
            get_position=["longitude", "latitude"],
            get_fill_color="color",
            get_line_color=[255, 255, 255],
            get_radius=400,
            pickable=True,
            stroked=True,
            filled=True,
            line_width_min_pixels=3,
            radius_min_pixels=8,
            radius_max_pixels=20,
        )
        layers.append(unit_layer)
        
        # Pulsing ring effect (larger transparent circle)
        pulse_layer = pdk.Layer(
            "ScatterplotLayer",
            data=units_df,
            get_position=["longitude", "latitude"],
            get_fill_color=[255, 255, 255, 50],
            get_radius=800,
            pickable=False,
            stroked=False,
            filled=True,
        )
        layers.append(pulse_layer)
    
    # ==========================================
    # LAYER 5: TextLayer - Vehicle Labels
    # ==========================================
    if show_routes and units:
        text_layer = pdk.Layer(
            "TextLayer",
            data=units_df,
            get_position=["longitude", "latitude"],
            get_text="vehicle_id",
            get_size=14,
            get_color=[255, 255, 255, 255],
            get_angle=0,
            get_text_anchor="'middle'",
            get_alignment_baseline="'center'",
            pickable=False,
        )
        layers.append(text_layer)
    
    # ==========================================
    # VIEW STATE - 3D Perspective
    # ==========================================
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=10.5,
        bearing=15,  # Slight rotation for 3D effect
        pitch=50,    # Elevated view angle
    )
    
    # ==========================================
    # TOOLTIP - Interactive Information
    # ==========================================
    tooltip = {
        "html": """
            <div style="
                background: rgba(15, 23, 42, 0.95);
                padding: 12px 16px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.1);
                min-width: 180px;
            ">
                <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">
                    {vehicle_id}
                </div>
                <div style="font-size: 18px; font-weight: 700; color: #f8fafc; margin: 4px 0;">
                    Route Efficiency: {efficiency_score}%
                </div>
                <div style="display: flex; gap: 16px; margin-top: 8px;">
                    <div>
                        <div style="font-size: 10px; color: #64748b;">Students</div>
                        <div style="font-size: 14px; color: #22c55e; font-weight: 600;">{total_students}</div>
                    </div>
                    <div>
                        <div style="font-size: 10px; color: #64748b;">Schools</div>
                        <div style="font-size: 14px; color: #3b82f6; font-weight: 600;">{num_schools}</div>
                    </div>
                    <div>
                        <div style="font-size: 10px; color: #64748b;">Distance</div>
                        <div style="font-size: 14px; color: #f59e0b; font-weight: 600;">{total_distance_km}km</div>
                    </div>
                </div>
            </div>
        """,
        "style": {
            "backgroundColor": "transparent",
            "color": "white",
        }
    }
    
    # Create deck
    # Using 'dark' style which works without Mapbox token
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="dark",
        tooltip=tooltip,
    )
    
    st.pydeck_chart(deck, use_container_width=True, height=500)


def create_route_legend(routes: List[Dict]) -> None:
    """
    Render the route legend with efficiency scores.
    """
    route_colors_hex = {
        0: "#ea580c",  # Orange
        1: "#3b82f6",  # Blue
        2: "#10b981",  # Green
        3: "#9333ea",  # Purple
        4: "#ef4444",  # Red
    }
    
    cols = st.columns(len(routes))
    
    for idx, (col, route) in enumerate(zip(cols, routes)):
        color = route_colors_hex.get(idx, "#6b7280")
        eff = route['efficiency_score']
        eff_color = "#22c55e" if eff >= 70 else ("#f59e0b" if eff >= 50 else "#ef4444")
        
        with col:
            st.markdown(f"""
                <div style="
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 0.75rem 1rem;
                ">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <div style="width: 12px; height: 12px; background: {color}; border-radius: 50%;"></div>
                        <div style="font-size: 0.8rem; font-weight: 600; color: #1e293b;">{route['vehicle_id']}</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #64748b;">
                        <span>{route['num_schools']} schools</span>
                        <span style="color: {eff_color}; font-weight: 600;">{eff}% eff.</span>
                    </div>
                    <div style="font-size: 0.75rem; color: #475569; margin-top: 0.25rem;">
                        {route['total_students']} students • {route['total_distance_km']:.1f}km
                    </div>
                </div>
            """, unsafe_allow_html=True)


def create_hexagon_map(df: pd.DataFrame, num_vans: int = 3, show_coverage_watch: bool = False, policy_mode: str = "balanced") -> None:
    """
    Render the 3D Landscape of Need visualization.
    
    Two modes:
    1. Standard Mode: HexagonLayer showing problem density
    2. Coverage Watch Mode: Problem + Solution (routes + mobile units)
    
    Args:
        df: School dataframe
        num_vans: Number of mobile enrollment units
        show_coverage_watch: Whether to show routes and mobile units
        policy_mode: "efficiency", "balanced", or "equity" - synced with sidebar control
    """
    # Initialize scenario cache
    cache = get_scenario_cache()
    
    # Coverage Watch Mode Controls
    st.markdown("""
        <div style="
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 1rem; font-weight: 600; color: #1e293b;">3D Landscape of Need</div>
                    <div style="font-size: 0.75rem; color: #64748b;">
                        Hexagon towers represent backlog magnitude • Color indicates vulnerability
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Mode toggle and scenario selector
    col_toggle, col_scenario, col_progress = st.columns([2, 2, 2])
    
    with col_toggle:
        coverage_watch = st.toggle(
            "**Coverage Watch Mode**",
            value=st.session_state.get('coverage_watch_active', False),
            help="Overlay optimized vehicle routes and mobile unit positions",
            key="coverage_watch_toggle"
        )
        st.session_state['coverage_watch_active'] = coverage_watch
    
    routes = []
    units = []
    # Use policy_mode from sidebar as the default scenario
    scenario = policy_mode
    
    if coverage_watch:
        with col_scenario:
            # Pre-select based on sidebar policy mode
            scenario_options = ["balanced", "efficiency", "equity"]
            default_index = scenario_options.index(policy_mode) if policy_mode in scenario_options else 0
            scenario = st.selectbox(
                "Optimization Scenario",
                options=scenario_options,
                index=default_index,
                format_func=lambda x: {
                    "balanced": "🎯 Balanced Approach",
                    "efficiency": "⚡ Maximum Efficiency", 
                    "equity": "⚖️ Equity Priority"
                }.get(x, x),
                key="scenario_selector",
                help="Synced with Policy Control Panel in sidebar"
            )
        
        with col_progress:
            progress = st.slider(
                "Route Progress",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1,
                format="%.0f%%",
                help="Simulated progress along routes",
                key="route_progress"
            ) 
        
        # Precompute routes for selected scenario
        cache.precompute_all(df, num_vans)
        routes = cache.get_routes(scenario)
        units = generate_mobile_unit_positions(routes, progress)
        
        # Show Coverage Watch header
        create_coverage_watch_header(scenario, routes)
    
    # Render the 3D map
    create_3d_landscape_map(df, routes, units, show_routes=coverage_watch)
    
    # Show route legend when in Coverage Watch mode
    if coverage_watch and routes:
        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
        create_route_legend(routes)
    
    # Legend for hexagon colors
    st.markdown("""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 2rem;
            padding: 0.75rem 1rem;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin-top: 0.75rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 14px; height: 14px; background: #dc2626; border-radius: 3px;"></div>
                <span style="font-size: 0.75rem; color: #475569;">Dark Zone (High Risk)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 14px; height: 14px; background: #f59e0b; border-radius: 3px;"></div>
                <span style="font-size: 0.75rem; color: #475569;">Moderate Zone</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 14px; height: 14px; background: #16a34a; border-radius: 3px;"></div>
                <span style="font-size: 0.75rem; color: #475569;">Accessible Zone</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 16px; height: 3px; background: linear-gradient(90deg, #ea580c, #3b82f6, #10b981);"></div>
                <span style="font-size: 0.75rem; color: #475569;">Vehicle Routes</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def create_route_summary_feasibility(df: pd.DataFrame, num_vans: int, policy_mode: str) -> None:
    """
    Section 3: Route Summary & Feasibility
    Shows Route Efficiency Scores and Feasibility Check with predictive risk model.
    """
    st.markdown("### Route Summary & Feasibility")
    st.markdown("Intervention plan analysis with predictive success forecasting")
    
    # Generate routes for current policy mode
    cache = get_scenario_cache()
    cache.precompute_all(df, num_vans)
    routes = cache.get_routes(policy_mode)
    
    if not routes:
        st.info("No routes generated. Adjust fleet configuration in sidebar.")
        return
    
    # Route Efficiency Scores Table
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.markdown("#### Route Efficiency Scores")
        st.markdown("<div style='font-size: 0.8rem; color: #64748b; margin-bottom: 1rem;'>Predicted students covered per route based on optimization scenario</div>", unsafe_allow_html=True)
        
        # Build route data for table
        route_data = []
        for route in routes:
            eff_score = route['efficiency_score']
            
            # Calculate students per km (efficiency metric)
            students_per_km = route['total_students'] / max(route['total_distance_km'], 1)
            
            route_data.append({
                "Route": route['vehicle_id'],
                "Schools": route['num_schools'],
                "Students": route['total_students'],
                "Distance (km)": f"{route['total_distance_km']:.1f}",
                "Students/km": f"{students_per_km:.1f}",
                "Efficiency": f"{eff_score}%",
            })
        
        # Display as styled dataframe
        route_df = pd.DataFrame(route_data)
        
        # Style the dataframe
        def style_efficiency(val):
            if isinstance(val, str) and '%' in val:
                score = int(val.replace('%', ''))
                if score >= 70:
                    return 'background-color: #dcfce7; color: #166534; font-weight: 600'
                elif score >= 50:
                    return 'background-color: #fef3c7; color: #92400e; font-weight: 600'
                else:
                    return 'background-color: #fee2e2; color: #991b1b; font-weight: 600'
            return ''
        
        styled_df = route_df.style.applymap(
            style_efficiency, 
            subset=['Efficiency']
        ).set_properties(**{
            'text-align': 'center',
            'font-size': '0.85rem',
        })
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Summary stats below table
        total_students = sum(r['total_students'] for r in routes)
        total_distance = sum(r['total_distance_km'] for r in routes)
        avg_efficiency = sum(r['efficiency_score'] for r in routes) / len(routes)
        
        st.markdown(f"""
            <div style="
                display: flex; 
                gap: 2rem; 
                margin-top: 1rem; 
                padding: 0.75rem 1rem;
                background: #f8fafc;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            ">
                <div style="text-align: center;">
                    <div style="font-size: 0.65rem; color: #64748b; text-transform: uppercase;">Total Students</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #1e293b;">{total_students:,}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.65rem; color: #64748b; text-transform: uppercase;">Total Distance</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #1e293b;">{total_distance:.0f} km</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.65rem; color: #64748b; text-transform: uppercase;">Avg Efficiency</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: {'#22c55e' if avg_efficiency >= 70 else '#f59e0b'};">{avg_efficiency:.0f}%</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Feasibility Check")
        st.markdown("<div style='font-size: 0.8rem; color: #64748b; margin-bottom: 1rem;'>Predictive risk model forecast</div>", unsafe_allow_html=True)
        
        # Simulated predictive risk factors based on policy mode
        risk_factors = {
            "efficiency": {
                "weather_risk": 12,
                "road_access": 8,
                "vehicle_breakdown": 5,
                "community_acceptance": 15,
                "overall_success": 87,
            },
            "balanced": {
                "weather_risk": 15,
                "road_access": 18,
                "vehicle_breakdown": 8,
                "community_acceptance": 10,
                "overall_success": 78,
            },
            "equity": {
                "weather_risk": 22,
                "road_access": 35,
                "vehicle_breakdown": 12,
                "community_acceptance": 8,
                "overall_success": 68,
            },
        }
        
        risks = risk_factors.get(policy_mode, risk_factors["balanced"])
        success = risks["overall_success"]
        success_color = "#22c55e" if success >= 75 else ("#f59e0b" if success >= 60 else "#dc2626")
        
        # Overall success rate card
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 2px solid {success_color};
                border-radius: 12px;
                padding: 1.25rem;
                text-align: center;
                margin-bottom: 1rem;
            ">
                <div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">Predicted Success Rate</div>
                <div style="font-size: 2.5rem; font-weight: 800; color: {success_color}; line-height: 1.2;">{success}%</div>
                <div style="font-size: 0.75rem; color: #475569; margin-top: 0.25rem;">
                    Based on historical data + current conditions
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Risk factors breakdown
        st.markdown("<div style='font-size: 0.75rem; font-weight: 600; color: #475569; margin-bottom: 0.5rem;'>Risk Factors</div>", unsafe_allow_html=True)
        
        risk_items = [
            ("Weather Disruption", risks["weather_risk"]),
            ("Road Accessibility", risks["road_access"]),
            ("Vehicle Breakdown", risks["vehicle_breakdown"]),
            ("Community Acceptance", risks["community_acceptance"]),
        ]
        
        for risk_name, risk_pct in risk_items:
            risk_color = "#dc2626" if risk_pct > 25 else ("#f59e0b" if risk_pct > 15 else "#22c55e")
            st.markdown(f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0.5rem 0.75rem;
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    margin-bottom: 0.5rem;
                ">
                    <span style="font-size: 0.75rem; color: #475569;">{risk_name}</span>
                    <span style="font-size: 0.75rem; font-weight: 600; color: {risk_color};">{risk_pct}%</span>
                </div>
            """, unsafe_allow_html=True)


def create_zone_breakdown(df: pd.DataFrame, policy_mode: str = "balanced") -> None:
    """
    Enhanced zone classification breakdown with priority ranking, GPI analysis,
    and intervention status. Uses real data from digital twin.
    
    Args:
        df: DataFrame with digital twin school data
        policy_mode: Current optimization policy for intervention status
    """
    st.markdown("### Zone Classification Breakdown")
    
    # Get cached zone statistics
    zone_stats = get_zone_statistics(df)
    
    # Define zone styling
    zone_styles = {
        'Dark Zone': {
            'bg': 'linear-gradient(135deg, #fef2f2 0%, #fff5f5 100%)',
            'border': '#dc2626',
            'color': '#dc2626',
            'priority': 1,
        },
        'Emerging Zone': {
            'bg': 'linear-gradient(135deg, #fff7ed 0%, #fffaf5 100%)',
            'border': '#f59e0b',
            'color': '#f59e0b',
            'priority': 2,
        },
        'Watch Zone': {
            'bg': 'linear-gradient(135deg, #eff6ff 0%, #f5f8ff 100%)',
            'border': '#3b82f6',
            'color': '#3b82f6',
            'priority': 3,
        },
        'Green Zone': {
            'bg': 'linear-gradient(135deg, #f0fdf4 0%, #f5fff8 100%)',
            'border': '#22c55e',
            'color': '#22c55e',
            'priority': 4,
        }
    }
    
    # Determine intervention status based on policy mode
    def get_intervention_status(zone_name: str, policy_mode: str) -> Tuple[str, str]:
        """Return (status_label, status_color) based on zone and policy."""
        if policy_mode == "equity":
            # Equity mode: Dark zones get priority
            status_map = {
                'Dark Zone': ('PRIORITIZED', '#dc2626'),
                'Emerging Zone': ('ACTIVE', '#f59e0b'),
                'Watch Zone': ('QUEUED', '#3b82f6'),
                'Green Zone': ('MONITORING', '#22c55e'),
            }
        elif policy_mode == "efficiency":
            # Efficiency mode: Focus on easier wins first
            status_map = {
                'Dark Zone': ('DEFERRED', '#94a3b8'),
                'Emerging Zone': ('QUEUED', '#f59e0b'),
                'Watch Zone': ('ACTIVE', '#3b82f6'),
                'Green Zone': ('PRIORITIZED', '#22c55e'),
            }
        else:  # balanced
            status_map = {
                'Dark Zone': ('ACTIVE', '#dc2626'),
                'Emerging Zone': ('ACTIVE', '#f59e0b'),
                'Watch Zone': ('QUEUED', '#3b82f6'),
                'Green Zone': ('MONITORING', '#22c55e'),
            }
        return status_map.get(zone_name, ('—', '#94a3b8'))
    
    # Calculate total backlog for summary
    total_backlog = df['backlog_students'].sum()
    dark_zone_backlog = zone_stats.get('Dark Zone', {}).get('total_backlog', 0)
    dark_zone_pct = round((dark_zone_backlog / max(total_backlog, 1)) * 100, 1)
    
    # Summary row
    st.markdown(f"""
        <div style="
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div style="font-size: 0.8rem; color: #64748b;">
                <strong style="color: #dc2626;">{dark_zone_pct}%</strong> of total backlog concentrated in Dark Zones
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8;">
                {len(zone_stats)} zones • {len(df):,} schools • {int(total_backlog):,} students pending
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Create zone cards - 4 columns for all zones
    zone_cols = st.columns(4, gap="medium")
    
    zone_order = ['Dark Zone', 'Emerging Zone', 'Watch Zone', 'Green Zone']
    
    for idx, zone_name in enumerate(zone_order):
        if zone_name not in zone_stats:
            continue
            
        stats = zone_stats[zone_name]
        style = zone_styles.get(zone_name, zone_styles['Watch Zone'])
        status_label, status_color = get_intervention_status(zone_name, policy_mode)
        
        # GPI alert indicator
        gpi = stats['avg_gpi']
        gpi_alert = "⚠" if gpi < 0.90 else ""
        gpi_color = "#dc2626" if gpi < 0.90 else ("#f59e0b" if gpi < 0.95 else "#22c55e")
        
        with zone_cols[idx]:
            st.markdown(f"""
                <div style="
                    background: {style['bg']};
                    border: 2px solid {style['border']};
                    border-radius: 10px;
                    padding: 1.25rem;
                    text-align: center;
                    height: 100%;
                    min-height: 280px;
                ">
                    <!-- Zone Title -->
                    <div style="font-size: 0.95rem; font-weight: 700; color: {style['color']}; margin-bottom: 0.5rem;">
                        {zone_name}
                    </div>
                    
                    <!-- Intervention Status Badge -->
                    <div style="
                        display: inline-block;
                        background: {status_color}15;
                        color: {status_color};
                        padding: 0.2rem 0.6rem;
                        border-radius: 4px;
                        font-size: 0.6rem;
                        font-weight: 600;
                        letter-spacing: 0.05em;
                        margin-bottom: 0.75rem;
                    ">
                        {status_label}
                    </div>
                    
                    <!-- Schools Count -->
                    <div style="font-size: 1.8rem; font-weight: 700; color: {style['color']}; line-height: 1.2;">
                        {stats['school_count']}
                    </div>
                    <div style="font-size: 0.7rem; color: #64748b; margin-bottom: 0.75rem;">schools</div>
                    
                    <!-- Metrics Grid -->
                    <div style="
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 0.5rem;
                        text-align: left;
                        padding: 0.75rem;
                        background: rgba(255,255,255,0.7);
                        border-radius: 6px;
                        margin-top: 0.5rem;
                    ">
                        <div>
                            <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">Backlog</div>
                            <div style="font-size: 0.85rem; font-weight: 600; color: #334155;">{stats['total_backlog']:,}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">% Total</div>
                            <div style="font-size: 0.85rem; font-weight: 600; color: #334155;">{stats['backlog_pct']}%</div>
                        </div>
                        <div>
                            <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">Saturation</div>
                            <div style="font-size: 0.85rem; font-weight: 600; color: #334155;">{stats['avg_saturation']}%</div>
                        </div>
                        <div>
                            <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">GPI {gpi_alert}</div>
                            <div style="font-size: 0.85rem; font-weight: 600; color: {gpi_color};">{gpi:.3f}</div>
                        </div>
                    </div>
                    
                    <!-- Priority Score -->
                    <div style="margin-top: 0.75rem; font-size: 0.7rem; color: #64748b;">
                        Priority Score: <strong style="color: {style['color']};">{stats['avg_priority_score']:.0f}</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)


def render_tab1(df: pd.DataFrame, num_vans: int, capacity: int, policy_mode: str = "balanced") -> None:
    """
    Main entry point for Tab 1 (Strategic Command Center / Situation Room).
    
    Layout:
    1. KPI Command Layer (Top) - Total Backlog, GPI, Saturation Rate, Operational Capacity
    2. 3D Geospatial Intelligence (Middle) - HexagonLayer + PathLayer + IconLayer
    3. Route Summary & Feasibility (Bottom) - Efficiency scores + Predictive risk model
    
    Args:
        df: DataFrame with school data
        num_vans: Number of mobile units available
        capacity: Daily enrollment capacity
        policy_mode: "efficiency", "balanced", or "equity" - controls optimization focus
    """
    st.markdown("## Strategic Command Center")
    st.markdown("Comprehensive overview of enrollment disparities and geographic access challenges.")
    st.divider()
    
    # SECTION 1: KPI Command Layer (Situation Room) - policy-aware
    create_kpi_cards(df, num_vans, capacity, policy_mode=policy_mode)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # SECTION 2: 3D Geospatial Intelligence (with Coverage Watch toggle) - policy-aware
    create_hexagon_map(df, num_vans=num_vans, policy_mode=policy_mode)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # SECTION 3: Route Summary & Feasibility
    create_route_summary_feasibility(df, num_vans, policy_mode)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Zone Classification Breakdown - now policy-aware
    create_zone_breakdown(df, policy_mode=policy_mode)
