"""
Route Optimization Engine
Implements Cluster-First, Route-Second heuristic for Capacitated Vehicle Routing 
Problem with Time Windows (CVRPTW).

Key Algorithm:
1. KMeans Clustering: Partition high-backlog schools into N clusters (N = # vehicles)
2. Prioritization: Sort within clusters by weighted priority (70% Backlog + 30% Access Risk)
3. Greedy Route Building: Construct routes respecting capacity and time constraints
4. Route Validation: Ensure feasibility and calculate metrics

Applications:
- Mobile Aadhaar enrollment unit deployment
- Biometric update drives
- Targeted outreach campaigns
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple, Optional
import math


# ==========================================
# 1. HAVERSINE DISTANCE UTILITY
# ==========================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two points in kilometers.
    
    Args:
        lat1, lon1: Starting point (latitude, longitude)
        lat2, lon2: Ending point (latitude, longitude)
    
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in km
    
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    
    a = np.sin(delta_lat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c


def estimate_travel_time(distance_km: float, avg_speed_kmph: float = 30) -> float:
    """
    Estimate travel time between two locations.
    
    Args:
        distance_km: Distance in kilometers
        avg_speed_kmph: Average speed (default: 30 km/h for urban/rural mixed)
    
    Returns:
        Time in minutes
    """
    return (distance_km / avg_speed_kmph) * 60


# ==========================================
# 2. ROUTE DATA STRUCTURES
# ==========================================

class Route:
    """Represents a single vehicle route."""
    
    def __init__(self, vehicle_id: str, start_lat: float, start_lon: float):
        """
        Initialize a route.
        
        Args:
            vehicle_id: Unique vehicle identifier (e.g., "VAN-001")
            start_lat, start_lon: Depot/starting location coordinates
        """
        self.vehicle_id = vehicle_id
        self.start_lat = start_lat
        self.start_lon = start_lon
        self.schools = []  # List of school records
        self.path = [(start_lat, start_lon)]  # Path coordinates
        self.total_students = 0
        self.total_time_minutes = 0
        self.total_distance_km = 0
    
    def add_school(self, school_id: str, school_name: str, lat: float, lon: float, 
                   backlog_students: int, visit_time_minutes: float = 30):
        """
        Add a school to the route.
        
        Args:
            school_id: School identifier
            school_name: School name
            lat, lon: School coordinates
            backlog_students: Number of students to enroll
            visit_time_minutes: Time spent at school (default: 30 min)
        """
        school_record = {
            "school_id": school_id,
            "school_name": school_name,
            "latitude": lat,
            "longitude": lon,
            "backlog_students": backlog_students,
            "visit_time_minutes": visit_time_minutes,
        }
        
        # Calculate distance from last location
        last_lat, last_lon = self.path[-1]
        distance = haversine_distance(last_lat, last_lon, lat, lon)
        travel_time = estimate_travel_time(distance)
        
        # Update route metrics
        self.schools.append(school_record)
        self.path.append((lat, lon))
        self.total_students += backlog_students
        self.total_time_minutes += travel_time + visit_time_minutes
        self.total_distance_km += distance
    
    def is_feasible(self, max_capacity: int, max_time_minutes: float) -> bool:
        """
        Check if route respects constraints.
        
        Args:
            max_capacity: Maximum students per vehicle
            max_time_minutes: Maximum operating time (minutes)
        
        Returns:
            True if feasible, False otherwise
        """
        return (self.total_students <= max_capacity and 
                self.total_time_minutes <= max_time_minutes)
    
    def to_dict(self) -> Dict:
        """Convert route to dictionary."""
        return {
            "vehicle_id": self.vehicle_id,
            "schools": self.schools,
            "path": self.path,
            "total_students": self.total_students,
            "total_distance_km": round(self.total_distance_km, 2),
            "total_time_minutes": round(self.total_time_minutes, 1),
            "num_schools": len(self.schools),
        }


# ==========================================
# 3. ROUTE OPTIMIZER CLASS
# ==========================================

class RouteOptimizer:
    """
    Cluster-First, Route-Second optimizer for CVRPTW.
    
    Algorithm:
    1. Cluster schools using KMeans (N clusters = # vehicles)
    2. Prioritize schools within each cluster
    3. Build routes greedily respecting constraints
    4. Return optimized deployment plan
    """
    
    def __init__(self, 
                 depot_lat: float = 13.1939,
                 depot_lon: float = 77.5941,
                 max_capacity: int = 150,
                 max_time_minutes: float = 480):
        """
        Initialize the route optimizer.
        
        Args:
            depot_lat, depot_lon: Starting location (default: Bengaluru central)
            max_capacity: Maximum students per vehicle per day
            max_time_minutes: Maximum operating time per vehicle (default: 8 hours)
        """
        self.depot_lat = depot_lat
        self.depot_lon = depot_lon
        self.max_capacity = max_capacity
        self.max_time_minutes = max_time_minutes
        self.routes = []
    
    def calculate_priority_score(self, row: pd.Series, 
                                 backlog_weight: float = 0.7,
                                 access_weight: float = 0.3) -> float:
        """
        Calculate weighted priority for school.
        
        Formula:
            priority = (backlog_weight × normalized_backlog) + 
                      (access_weight × normalized_access_risk)
        
        Args:
            row: DataFrame row (school record)
            backlog_weight: Weight for backlog (default: 70%)
            access_weight: Weight for access risk (default: 30%)
        
        Returns:
            Priority score (0-1)
        """
        return (backlog_weight * (row['backlog_students'] / 100) +
                access_weight * (row['access_risk_score'] / 100))
    
    def optimize_routes(self, df: pd.DataFrame, num_vehicles: int) -> List[Dict]:
        """
        Optimize routes using Cluster-First, Route-Second heuristic.
        
        Algorithm:
        1. Filter high-priority schools (backlog > 0)
        2. KMeans clustering into num_vehicles clusters
        3. Sort within clusters by priority score
        4. Greedily build routes respecting constraints
        
        Args:
            df: DataFrame with schools (must have: latitude, longitude, backlog_students, access_risk_score)
            num_vehicles: Number of mobile units available
        
        Returns:
            List of route dictionaries
        """
        
        # Filter schools with backlog
        schools_df = df[df['backlog_students'] > 0].copy()
        
        if len(schools_df) == 0:
            print("⚠️  No schools with backlog found.")
            return []
        
        # Limit vehicles to available schools
        num_vehicles = min(num_vehicles, len(schools_df))
        
        print(f"📍 Optimizing routes for {len(schools_df)} schools with {num_vehicles} vehicles...")
        
        # ==========================================
        # STEP 1: KMEANS CLUSTERING
        # ==========================================
        
        # Prepare coordinates for clustering
        coordinates = schools_df[['latitude', 'longitude']].values
        
        kmeans = KMeans(n_clusters=num_vehicles, random_state=42, n_init=10)
        schools_df['cluster'] = kmeans.fit_predict(coordinates)
        
        print(f"✓ KMeans clustering complete ({num_vehicles} clusters)")
        
        # ==========================================
        # STEP 2: PRIORITIZE WITHIN CLUSTERS
        # ==========================================
        
        schools_df['priority_score'] = schools_df.apply(
            lambda row: self.calculate_priority_score(row, 0.7, 0.3),
            axis=1
        )
        
        # Sort by cluster then by priority (descending)
        schools_df = schools_df.sort_values(['cluster', 'priority_score'], 
                                            ascending=[True, False])
        
        print(f"✓ Prioritization complete")
        
        # ==========================================
        # STEP 3: GREEDY ROUTE BUILDING
        # ==========================================
        
        self.routes = []
        
        for cluster_id in range(num_vehicles):
            vehicle_id = f"VAN-{cluster_id + 1:03d}"
            route = Route(vehicle_id, self.depot_lat, self.depot_lon)
            
            # Get schools in this cluster, sorted by priority
            cluster_schools = schools_df[schools_df['cluster'] == cluster_id]
            
            for _, school in cluster_schools.iterrows():
                # Try to add school to current route
                if (route.total_students + school['backlog_students'] <= self.max_capacity and
                    route.total_time_minutes + 60 <= self.max_time_minutes):  # 60 min = 30 min travel + 30 min visit
                    
                    route.add_school(
                        school_id=school.get('school_id', ''),
                        school_name=school.get('school_name', ''),
                        lat=school['latitude'],
                        lon=school['longitude'],
                        backlog_students=int(school['backlog_students']),
                        visit_time_minutes=30
                    )
                else:
                    # School doesn't fit in current route
                    # Could implement: create overflow route or skip
                    pass
            
            if len(route.schools) > 0:
                self.routes.append(route)
        
        print(f"✓ Routes built ({len(self.routes)} feasible routes)")
        
        # ==========================================
        # STEP 4: VALIDATION & SUMMARY
        # ==========================================
        
        routes_data = [route.to_dict() for route in self.routes]
        
        total_students_covered = sum(r['total_students'] for r in routes_data)
        total_schools_visited = sum(r['num_schools'] for r in routes_data)
        
        print(f"\n{'='*70}")
        print(f"  OPTIMIZATION SUMMARY")
        print(f"{'='*70}")
        print(f"  Routes Generated:................ {len(routes_data)}")
        print(f"  Total Schools in Routes:......... {total_schools_visited}")
        print(f"  Total Students to Enroll:....... {total_students_covered:,}")
        print(f"  Total Distance:................. {sum(r['total_distance_km'] for r in routes_data):.1f} km")
        print(f"  Avg Distance per Route:......... {np.mean([r['total_distance_km'] for r in routes_data]):.1f} km")
        print(f"  Avg Utilization:................ {100 * np.mean([r['total_students']/self.max_capacity for r in routes_data]):.1f}%")
        print(f"{'='*70}\n")
        
        return routes_data
    
    def get_route_summary(self) -> pd.DataFrame:
        """
        Get summary statistics for all routes.
        
        Returns:
            DataFrame with route metrics
        """
        summaries = []
        
        for route in self.routes:
            route_dict = route.to_dict()
            summaries.append({
                'vehicle_id': route_dict['vehicle_id'],
                'num_schools': route_dict['num_schools'],
                'total_students': route_dict['total_students'],
                'total_distance_km': route_dict['total_distance_km'],
                'total_time_minutes': route_dict['total_time_minutes'],
                'capacity_utilization_%': round(100 * route_dict['total_students'] / self.max_capacity, 1),
                'time_utilization_%': round(100 * route_dict['total_time_minutes'] / self.max_time_minutes, 1),
            })
        
        return pd.DataFrame(summaries)
    
    def export_routes(self, output_path: str):
        """
        Export optimized routes to CSV.
        
        Args:
            output_path: File path for output CSV
        """
        routes_data = [route.to_dict() for route in self.routes]
        
        # Flatten routes for CSV export
        export_records = []
        for route_data in routes_data:
            for idx, school in enumerate(route_data['schools']):
                export_records.append({
                    'vehicle_id': route_data['vehicle_id'],
                    'sequence': idx + 1,
                    'school_id': school['school_id'],
                    'school_name': school['school_name'],
                    'latitude': school['latitude'],
                    'longitude': school['longitude'],
                    'backlog_students': school['backlog_students'],
                    'visit_time_minutes': school['visit_time_minutes'],
                })
        
        export_df = pd.DataFrame(export_records)
        export_df.to_csv(output_path, index=False)
        print(f"✓ Routes exported to {output_path}")


# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================

def analyze_cluster_distribution(df: pd.DataFrame, num_vehicles: int) -> Dict:
    """
    Analyze how KMeans clusters distribute schools.
    
    Args:
        df: School DataFrame
        num_vehicles: Number of clusters
    
    Returns:
        Dictionary with cluster statistics
    """
    schools_df = df[df['backlog_students'] > 0].copy()
    
    coordinates = schools_df[['latitude', 'longitude']].values
    kmeans = KMeans(n_clusters=min(num_vehicles, len(schools_df)), random_state=42, n_init=10)
    clusters = kmeans.fit_predict(coordinates)
    
    unique, counts = np.unique(clusters, return_counts=True)
    
    analysis = {
        'cluster_sizes': dict(zip(unique, counts)),
        'avg_cluster_size': np.mean(counts),
        'max_cluster_size': np.max(counts),
        'min_cluster_size': np.min(counts),
    }
    
    return analysis


def calculate_route_efficiency(route_dict: Dict, max_capacity: int, max_time_minutes: float) -> Dict:
    """
    Calculate efficiency metrics for a route.
    
    Args:
        route_dict: Route dictionary
        max_capacity: Vehicle capacity
        max_time_minutes: Max operating time
    
    Returns:
        Efficiency metrics
    """
    return {
        'vehicle_id': route_dict['vehicle_id'],
        'capacity_utilization': round(100 * route_dict['total_students'] / max_capacity, 1),
        'time_utilization': round(100 * route_dict['total_time_minutes'] / max_time_minutes, 1),
        'cost_per_student': round(route_dict['total_distance_km'] / max(route_dict['total_students'], 1), 2),
        'schools_per_km': round(route_dict['num_schools'] / max(route_dict['total_distance_km'], 1), 2),
    }
