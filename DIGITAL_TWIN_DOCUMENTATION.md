# Digital Twin Data Engine - Technical Documentation

## Overview

The **Digital Twin Data Engine** generates a high-fidelity synthetic dataset simulating school-level Aadhaar enrollment patterns. It models:

- **Invisible Backlog**: Age-15 cohorts not yet enrolled
- **Rural/Urban Disparities**: Access barriers & infrastructure gaps
- **Gender Parity Issues**: Female underrepresentation (GPI < 0.9)
- **Enrollment Centers**: Fixed 5-hub deployment model
- **Access Risk Zones**: Dark zones (severely underserved)

---

## Key Concepts

### 1. Age-15 Cohort (Target Group)

**Definition**: The eligible population for Aadhaar enrollment in a given school year.

**Estimation Logic**:
```
age_15_cohort = total_students × [8%, 10%)
```

- Typically 8-10% of total school enrollment
- Represents the "invisible backlog" before enrollment begins
- Core input for backlog calculation

**Example**:
- School with 500 total students
- Cohort size: 500 × 0.09 = 45 students (target group)

---

### 2. Saturation Rate (Enrollment Coverage)

**Definition**: Proportion of the age-15 cohort already enrolled in Aadhaar.

**Distribution**: Beta(α=5, β=2)
- Produces realistic, right-skewed distribution
- Most schools achieve 60-90% saturation
- Allows for both high-performing and struggling schools

**Formula**:
```
saturation_rate ~ Beta(α=5, β=2)

If rural:
  saturation_rate = saturation_rate × (1 - 0.15)  # Apply 15% penalty
```

**Rural Penalty**: 0.15 factor
- Simulates access barriers (distance, transportation, awareness)
- Rural schools average ~15% lower saturation
- Example: Urban school 80% saturation → Rural school 68% saturation (68 = 80 × 0.85)

---

### 3. Backlog Estimation

**Definition**: Number of age-15 students NOT yet enrolled in Aadhaar.

**Formula**:
```
backlog_students = age_15_cohort × (1 - saturation_rate)

Example:
  Cohort: 45 students
  Saturation: 70%
  Backlog: 45 × (1 - 0.70) = 45 × 0.30 = 13.5 ≈ 14 students
```

**Status Classification**:
- **CRITICAL**: Backlog > 75th percentile (high enrollment gap)
- **NORMAL**: Backlog ≤ 75th percentile

---

### 4. Gender Parity Index (GPI)

**Definition**: Ratio of female-to-male saturation rates.

**Formula**:
```
GPI = female_saturation / male_saturation

Example:
  Female saturation: 70%
  Male saturation: 80%
  GPI = 0.70 / 0.80 = 0.875
```

**Interpretation**:
- **GPI = 1.0**: Perfect parity (equal enrollment)
- **GPI < 0.9**: **Equity Risk Flag** (female underrepresentation)
- **GPI > 1.1**: Male underrepresentation (less common)

**SDG Alignment**: 
- UN Sustainable Development Goal 5 (Gender Equality)
- Target: GPI ≥ 0.95 in all schools

---

### 5. Access Risk Score

**Definition**: Distance-based metric measuring accessibility to enrollment centers.

**Calculation**:
```
1. Calculate distance from school to each of 5 fixed enrollment centers
2. Find minimum distance (nearest center)
3. Normalize to 0-100 scale:

   access_risk_score = (min_distance_km / max_distance_km) × 100

   Where max_distance_km = 50 km (threshold for maximum risk)
```

**Zone Classification**:
- **Accessible** (0-50): Within 25 km of center
- **Moderate Access** (50-75): 25-37.5 km from center
- **Dark Zone** (75-100): > 37.5 km from center (severely underserved)

**Example**:
- School 12 km from nearest center: (12/50) × 100 = 24 (Accessible)
- School 40 km from nearest center: (40/50) × 100 = 80 (Dark Zone)

---

### 6. Fixed Enrollment Centers

The data engine simulates **5 major enrollment hubs**:

| Center ID | Name | Lat | Lon | Coverage Zone |
|-----------|------|-----|-----|----------------|
| CENTER_1 | Bengaluru Central | 13.1939 | 77.5941 | Downtown |
| CENTER_2 | Whitefield Hub | 13.0827 | 77.6254 | IT Corridor |
| CENTER_3 | Indiranagar | 13.1959 | 77.7049 | East |
| CENTER_4 | Electronic City | 12.9352 | 77.6245 | South |
| CENTER_5 | Devanahalli | 13.2328 | 77.4597 | North |

Each school's access risk is based on **distance to nearest center**.

---

### 7. Priority Score (Composite Urgency Metric)

**Definition**: Multi-factor urgency ranking for intervention prioritization.

**Formula**:
```
priority_score = 
  0.4 × backlog_weight +
  0.25 × access_weight +
  0.2 × saturation_weight +
  0.15 × equity_weight

Where:
  backlog_weight = min(backlog_students / 100, 1.0)
  access_weight = access_risk_score / 100
  saturation_weight = 1 - saturation_rate
  equity_weight = 1.0 if GPI < 0.9 else 0.0
```

**Weighting Rationale**:
- **40% Backlog**: Primary driver (absolute enrollment gap)
- **25% Access**: Geographic reach (supply-side constraint)
- **20% Saturation**: Relative progress (underperformance)
- **15% Equity**: Gender fairness (SDG alignment)

**Example**:
```
School A:
  backlog_weight: 0.8 (80 students in backlog)
  access_weight: 0.6 (60 risk score, moderate access)
  saturation_weight: 0.3 (70% saturation)
  equity_weight: 1.0 (GPI = 0.85, equity risk)
  
  priority_score = 0.4×0.8 + 0.25×0.6 + 0.2×0.3 + 0.15×1.0
                 = 0.32 + 0.15 + 0.06 + 0.15
                 = 0.68 (HIGH PRIORITY)
```

---

## Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| school_id | str | Unique identifier (SCH-10000, etc.) |
| school_name | str | Human-readable name |
| latitude | float | GPS latitude |
| longitude | float | GPS longitude |
| category | str | 'rural' or 'urban' |
| total_students | int | Total enrollment |
| age_15_cohort | int | Target enrollment group |
| female_students | int | Female enrollment |
| male_students | int | Male enrollment |
| saturation_rate | float | Coverage (0-1) |
| female_saturation | float | Female coverage (0-1) |
| male_saturation | float | Male coverage (0-1) |
| gender_parity_index | float | Female/Male ratio |
| equity_risk | bool | GPI < 0.9 flag |
| backlog_students | int | Unenrolled cohort |
| access_risk_score | float | Distance-based risk (0-100) |
| zone_label | str | 'Dark Zone', 'Moderate Access', 'Accessible' |
| priority_score | float | Composite urgency (0-1) |
| status | str | 'CRITICAL' or 'NORMAL' |

---

## Usage

### Generate Dataset

```python
from core.data_engine import generate_digital_twin_dataset

# Generate 200 schools
df = generate_digital_twin_dataset(n_schools=200, seed=42)

# Display first 5
print(df.head(5))
```

### Get Summary Statistics

```python
from core.data_engine import get_dataset_summary

summary = get_dataset_summary(df)
print(f"Total backlog: {summary['total_backlog']}")
print(f"Equity risk schools: {summary['equity_risk_schools']}")
print(f"Dark zones: {summary['dark_zones']}")
```

### Identify Priority Schools

```python
from core.data_engine import identify_priority_clusters

top_10 = identify_priority_clusters(df, top_n=10)
print(top_10)
```

### Run Validation

```bash
python core/validate_digital_twin.py
```

---

## Validation Routine

The `validate_digital_twin.py` script provides:

1. **Sample Records**: First 5 schools
2. **Summary Statistics**: Key metrics
3. **Rural vs Urban Analysis**: Disparity insights
4. **Enrollment Centers**: Hub locations
5. **Priority Clusters**: Top 10 urgent schools
6. **Data Distribution**: Backlog, saturation, GPI, access risk
7. **Zone Breakdown**: Dark zone prevalence
8. **Critical Insights**: High-risk combinations
9. **Dataset Export**: Save to CSV

---

## Realistic Parameters

### Beta Distribution (Saturation Rate)

**Choice of α=5, β=2**:
- Produces mean ≈ 0.71 (71% saturation)
- Right-skewed: most schools 60-90%
- Allows variance for underperforming schools
- Matches typical real-world Aadhaar enrollment patterns

### Rural Penalty (15%)

**Justification**:
- Rural schools face:
  - Longer distances to enrollment centers
  - Lower awareness/outreach
  - Transportation barriers
  - Infrastructure constraints
- 15% penalty reflects ~15-20% enrollment gap observed in field data

### Cohort Size (8-10%)

**Research-backed**:
- Age-15 cohort typically 8-10% of school enrollment
- Varies by state (varies 7-11% in reality)
- Ensures representative backlog sizes

### Access Risk Thresholds

- **25 km cutoff for urban/rural**: Administrative boundary
- **50 km max distance**: Regional deployment radius
- **75 risk score threshold**: Dark zone definition

---

## Integration with Dashboard

The generated dataset flows into:

1. **Overview Tab**: Summary metrics (total backlog, critical schools, etc.)
2. **Map View**: Heatmap overlay (access_risk_score, zone_label)
3. **Analytics Panel**: Top-priority schools (identify_priority_clusters)
4. **Route Optimization**: Backlog as demand input for vehicle routing
5. **Equity Dashboard**: GPI tracking and gender parity trends

---

## Next Steps (Phase 3)

- [ ] Connect to live DISHA dataset (pilot state)
- [ ] Validate against real enrollment patterns
- [ ] Tune penalty factors based on field feedback
- [ ] Add temporal dynamics (weekly enrollment trends)
- [ ] Integrate with UIDAI Gateway for real-time updates

---

**Data Engine Version**: 1.0  
**Last Updated**: January 2026  
**Maintainer**: Analytics Team
