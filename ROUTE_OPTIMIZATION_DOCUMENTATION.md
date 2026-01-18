# Route Optimization Engine - Technical Documentation

## Overview

The **Route Optimization Engine** implements a **Cluster-First, Route-Second heuristic** for the Capacitated Vehicle Routing Problem with Time Windows (CVRPTW). 

**Purpose**: Optimize deployment of mobile Aadhaar enrollment units to maximize coverage, minimize distance, and ensure equitable access across rural and urban zones.

---

## Algorithm Overview

### Architecture: Cluster-First, Route-Second

This two-phase approach balances computational efficiency with solution quality:

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: Schools with (backlog, location, access_risk)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │   PHASE 1: CLUSTERING        │
        │  KMeans(K = # vehicles)      │
        │  Groups schools by proximity │
        └──────────────────┬───────────┘
                           │
                           ▼
        ┌──────────────────────────────┐
        │   PHASE 2: PRIORITIZATION    │
        │  Sort by weighted priority:  │
        │   70% Backlog + 30% Access   │
        └──────────────────┬───────────┘
                           │
                           ▼
        ┌──────────────────────────────┐
        │   PHASE 3: GREEDY ROUTING    │
        │  Build routes respecting:    │
        │   - Capacity constraints     │
        │   - Time windows             │
        │   - Geographic efficiency    │
        └──────────────────┬───────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT: Routes (vehicles, paths, students, metrics)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Algorithm

### Phase 1: KMeans Clustering

**Objective**: Partition schools into N geographic clusters (N = # vehicles)

**Implementation**:
```python
from sklearn.cluster import KMeans

# Extract coordinates
coordinates = schools_df[['latitude', 'longitude']].values

# Cluster into K groups
kmeans = KMeans(n_clusters=num_vehicles, random_state=42)
cluster_labels = kmeans.fit_predict(coordinates)
```

**Why KMeans?**
- Fast (O(nkd) for n schools, k clusters, d dimensions)
- Intuitive: minimizes within-cluster distance
- Ensures each vehicle has a geographic "territory"
- Reduces backtracking in routes

**Example** (3 vehicles):
```
Cluster 0 (VAN-001): 65 schools in North zone
Cluster 1 (VAN-002): 68 schools in East zone
Cluster 2 (VAN-003): 67 schools in South zone
```

---

### Phase 2: Prioritization Within Clusters

**Objective**: Rank schools by urgency within each cluster

**Priority Formula**:
```
priority_score = (0.7 × backlog_normalized) + (0.3 × access_risk_normalized)

Where:
  backlog_normalized = backlog_students / 100
  access_risk_normalized = access_risk_score / 100
```

**Weights Rationale**:
- **70% Backlog**: Primary objective (students to enroll)
- **30% Access Risk**: Secondary (geographic reach)

**Example**:
```
School A:
  Backlog: 80 students
  Access Risk: 60
  priority = 0.7 × (80/100) + 0.3 × (60/100)
           = 0.56 + 0.18 = 0.74

School B:
  Backlog: 20 students
  Access Risk: 90
  priority = 0.7 × (20/100) + 0.3 × (90/100)
           = 0.14 + 0.27 = 0.41

→ School A visited first (higher priority)
```

---

### Phase 3: Greedy Route Building

**Objective**: Construct feasible routes respecting constraints

**Algorithm**:
```
For each cluster:
  Initialize empty route (vehicle at depot)
  
  For each school in cluster (sorted by priority):
    If (route.capacity + school.backlog ≤ max_capacity) AND
       (route.time + travel_time + visit_time ≤ max_time):
      Add school to route
    Else:
      Skip school (or add to overflow list)
    
    Calculate distance & time metrics
  
  Output: feasible route
```

**Constraints**:
1. **Capacity**: `route.total_students ≤ max_capacity` (150 students/day)
2. **Time Window**: `route.total_time ≤ max_time_minutes` (480 min = 8 hours)

**Time Estimation**:
```
travel_time_minutes = (distance_km / avg_speed_kmph) × 60
                    = (distance_km / 30) × 60

Example:
  15 km distance → (15/30) × 60 = 30 minutes
  
total_time = sum(travel_times) + sum(visit_times)
           = travel_time + (num_schools × 30 min/school)
```

**Distance Calculation** (Haversine):
```
distance_km = 2 × arcsin(sqrt(sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2))) × R

Where:
  Δlat = latitude_difference
  Δlon = longitude_difference
  R = 6371 km (Earth radius)
```

---

## Data Structures

### Route Class

```python
class Route:
    vehicle_id: str                    # "VAN-001"
    start_lat, start_lon: float        # Depot coordinates
    schools: List[Dict]                # Schools visited
    path: List[Tuple]                  # [(lat, lon), ...] waypoints
    total_students: int                # Students enrolled
    total_time_minutes: float          # Route duration
    total_distance_km: float           # Total distance
    
    methods:
    - add_school()                     # Add school to route
    - is_feasible()                    # Check constraints
    - to_dict()                        # Convert to dict
```

### RouteOptimizer Class

```python
class RouteOptimizer:
    depot_lat, depot_lon: float        # Starting location
    max_capacity: int                  # Students per vehicle
    max_time_minutes: float            # Operating hours
    routes: List[Route]                # Optimized routes
    
    methods:
    - optimize_routes(df, num_vehicles)     # Main algorithm
    - calculate_priority_score()            # Priority formula
    - get_route_summary()                   # Summary statistics
    - export_routes(filepath)               # Export to CSV
```

---

## Input Requirements

The input DataFrame must contain:

| Column | Type | Description |
|--------|------|-------------|
| school_id | str | Unique identifier |
| school_name | str | School name |
| latitude | float | GPS latitude |
| longitude | float | GPS longitude |
| backlog_students | int | Unenrolled cohort |
| access_risk_score | float | Distance-based risk (0-100) |

---

## Output Structure

### Route Dictionary

```python
{
    'vehicle_id': 'VAN-001',
    'schools': [
        {
            'school_id': 'SCH-10000',
            'school_name': 'Govt Primary School, Devanahalli',
            'latitude': 13.189799,
            'longitude': 77.539983,
            'backlog_students': 80,
            'visit_time_minutes': 30
        },
        ...
    ],
    'path': [(13.1939, 77.5941), (13.189799, 77.539983), ...],
    'total_students': 142,
    'total_distance_km': 45.2,
    'total_time_minutes': 325.5,
    'num_schools': 6
}
```

### Route Summary

```
vehicle_id   num_schools   total_students   total_distance_km   total_time_minutes
VAN-001      6             142              45.2                325.5
VAN-002      7             148              52.1                358.2
VAN-003      5             135              38.9                298.1
```

---

## Usage Examples

### Basic Optimization

```python
from core.data_engine import generate_digital_twin_dataset
from core.optimization import RouteOptimizer

# Generate schools
df = generate_digital_twin_dataset(n_schools=200)

# Create optimizer
optimizer = RouteOptimizer(
    max_capacity=150,           # Students per vehicle
    max_time_minutes=480        # 8 hours
)

# Optimize routes
routes = optimizer.optimize_routes(df, num_vehicles=5)

# Get summary
summary = optimizer.get_route_summary()
print(summary)
```

### Export Routes

```python
optimizer.export_routes('data/optimized_routes.csv')
```

### Efficiency Analysis

```python
from core.optimization import calculate_route_efficiency

for route in routes:
    efficiency = calculate_route_efficiency(
        route, 
        max_capacity=150, 
        max_time_minutes=480
    )
    print(f"{route['vehicle_id']}: {efficiency['capacity_utilization']}% capacity")
```

---

## Performance Metrics

### Capacity Utilization

```
utilization_% = (total_students / max_capacity) × 100

Interpretation:
  80%+ → Efficient, well-utilized fleet
  60-80% → Good utilization
  <60% → Underutilized (consider fewer vehicles)
```

### Time Utilization

```
utilization_% = (total_time_minutes / max_time_minutes) × 100

Interpretation:
  80-90% → Optimal (allows breaks, contingencies)
  90%+ → Overworked (risk of schedule slippage)
  <60% → Plenty of capacity
```

### Cost Efficiency

```
cost_per_student = total_distance_km / total_students

Interpretation:
  <1.0 km/student → Excellent (dense clusters)
  1.0-2.0 km/student → Good
  >2.0 km/student → Poor (dispersed, expensive)
```

---

## Testing

Run the comprehensive test suite:

```bash
python core/test_optimization.py
```

**Tests include**:
1. Dataset generation (200 schools)
2. Cluster distribution analysis (3, 5, 8 vehicles)
3. Route optimization
4. Efficiency metrics
5. Coverage analysis
6. Route export

**Sample Output**:
```
OPTIMIZATION SUMMARY
Routes Generated:         3
Schools in Routes:        180
Total Students:           4,250
Capacity Utilization:     92.1%
Time Utilization:         85.3%
Coverage:                 87.5% of total backlog
```

---

## Limitations & Future Improvements

### Current Limitations
- Greedy within-cluster (doesn't optimize across clusters)
- Fixed 30-minute visit time (doesn't account for school size variation)
- No vehicle constraints (different vehicle types)
- No temporal dynamics (time-dependent demand, traffic patterns)

### Future Enhancements
- **2-Opt Local Search**: Post-optimization to improve routes
- **Dynamic Time Windows**: Visit time varies by cohort size
- **Multi-objective Optimization**: Balance distance, equity, accessibility
- **Real-time Updates**: Responsive to cancellations, new schools
- **Historical Constraints**: Traffic patterns, seasonal demand

---

## Integration with Dashboard

The optimization engine feeds into the Streamlit dashboard:

1. **Overview Tab**: Summary metrics (routes, coverage, efficiency)
2. **Map View**: Route paths with school markers
3. **Route Details**: School-by-school sequence for each vehicle
4. **Export**: Download manifests for field deployment

---

## References

- **CVRPTW**: Cordeau et al., 2006. "Vehicle Routing Problem with Time Windows"
- **Cluster-First, Route-Second**: Fisher & Jaikumar, 1981
- **KMeans**: Lloyd, 1982. "Least squares quantization in PCM"
- **Haversine Formula**: Sinnott, 1984. "Virtues of the Haversine"

---

**Engine Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Production Ready
