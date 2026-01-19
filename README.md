<div align="center">
<img width="3840" height="2701" alt="image" src="https://github.com/user-attachments/assets/06d0c7a9-1ab4-4aac-aad4-377d614ceb89" />

# Vidyarthi-Raksha

**Intelligent Logistics Optimization for Aadhaar Enrolment & Update Missions**  
Strategic dashboards, tactical routing, and analytical intelligence in one Streamlit application.

[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b.svg)](https://streamlit.io/)  
**Status:** DEMO-ready (v1.0.0) • **Last Update:** 18 Jan 2026

</div>

## Table of Contents
- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Data Sources & Methodology](#data-sources--methodology)
- [Application Modules](#application-modules)
- [Scenario Planning Workflow](#scenario-planning-workflow)
- [Quick Start](#quick-start)
- [Repository Map](#repository-map)
- [Related Repositories](#related-repositories)
- [Validation & Success Metrics](#validation--success-metrics)
- [Documentation Index](#documentation-index)
- [Roadmap](#roadmap)

## Project Overview
Vidyarthi-Raksha connects **demand-side intelligence**, **supply-side capacity modelling**, and **actionable logistics** so UIDAI field teams know **where pressure exists, what resources are available, and which deployment decisions to take next**. The dashboard exposes three tailored workspaces:

| Persona | Goal | Tab |
| --- | --- | --- |
| Executives & policy makers | See national backlog risk, gender parity, and equity gaps | Strategic Command Center |
| Field coordinators | Assign mobile vans, monitor coverage, share manifests | Tactical Operations Center |
| Analysts & planners | Forecast clearance timelines, compare rural vs urban, flag equity alerts | Analytical Intelligence |

## System Architecture

```
Phase 2  →  Phase 3  →  Phase 4
Digital Twin   Route Optimization   Command Center UI
     ↑               ↑                    ↑
 Demand signals  +  CVRPTW solver  +  Streamlit UX4G theme
```

Core services:
- **Digital Twin Dataset** – 200 synthetic schools with backlog, saturation, GPI, and access risk metrics.
- **RouteOptimizer (CVRPTW)** – Cluster-first, priority-weighted vehicle routes honoring capacity & time windows.
- **Streamlit App** – `app.py` orchestrates sidebar controls, stateful scenario planning, and three view modules (`views/`).

## Data Sources & Methodology

### Demand Intelligence
| Dataset | Source | Derived Metrics |
| --- | --- | --- |
| UIDAI Enrolment & Update (Core) | UIDAI secure feeds | `biometric_obsolescence`, `update_velocity`, `backlog_growth_rate`, `seasonality_index` |
| UDISE+ School Infrastructure | Ministry of Education (UDISE+ Open Data) | `expected_mbu_demand = students_age_5 + students_age_15`, `school_risk_score` |
| Census / SRS Age Bands | Census of India & SRS | Validates age-band volumes, normalizes outliers, removes synthetic bias |

### Supply Intelligence
| Dataset | Source | Derived Metrics |
| --- | --- | --- |
| UIDAI Centre & Kit Availability | UIDAI centre locator | `daily_capacity`, `effective_capacity` (downtime adjusted) |
| Mobile Aadhaar Vans & Camps | Field ops manifests | Route-ready fleet inventory for CVRPTW solver |

### Master Dataset Schema (excerpt)
`school_id`, `school_name`, `lat`, `lon`, `district`, `pending_mbu`, `risk_level`, `distance_to_nearest_center`, `nearest_center_capacity`, `assigned_van_id`, `estimated_clearance_days`, `priority_score`.

### Methodology
- **Data Cleaning** – Deduplicated enrolment records, normalized age bands, clipped outliers via IQR.
- **Feature Engineering** – Risk score = weighted backlog + distance; rolling-average demand forecasts; explicit capacity constraints.
- **Reproducibility** – All transformations scripted in Python/Pandas with deterministic seeds and schema-first tracking.
- **Ethics & Privacy** – Aggregated, anonymized metrics only; no PII; conforms to UIDAI data-sharing norms.

## Application Modules

### Tab 1 – Strategic Command Center (`views/tab1_command.py`)
- KPI strip (Saturation MoM, Backlog Reduction, Enrollment Rate, Days to 95% saturation).
- PyDeck 3D “Landscape of Need” map + Coverage Watch overlay.
- Zone classification and dark-zone spotlight cards.

### Tab 2 – Tactical Operations Center (`views/tab2_operations.py`)
- Mapbox route visualization with van-specific colors.
- Gantt-style vehicle schedule, backlog coverage gauges, access-risk histograms.
- Manifest export primitives for field deployment.

### Tab 3 – Analytical Intelligence (`views/tab3_intelligence.py`)
- 12‑month backlog forecast chart with seasonal spikes.
- Gender Parity Index diverging bars (top 20 schools) and rural vs urban box plots.
- Equity alert summaries and dark-zone discovery narrative.

### Sidebar Scenario Console
- Fleet size (1–10 vans) & capacity (50–500 students/day).
- Policy priority slider (backlog vs access risk) auto-normalized.
- `Optimize Routes` button triggers RouteOptimizer → cached in `st.session_state` for reuse across tabs.
- Real-time capacity calculator and system status widget.

## Scenario Planning Workflow
1. **Adjust sliders** for vans, capacity, and backlog/access weighting.
2. **Click `🚀 Optimize Routes`** to run CVRPTW solver (KMeans clustering + greedy scheduling).
3. **Inspect Tactical tab** for route geometry, schedules, and coverage stats.
4. **Switch to Strategic / Analytical tabs** to confirm macro indicators and equity impacts.
5. **Iterate** until backlog clearance timeline meets mission targets.

## Quick Start

### Prerequisites
- Python 3.10+ (pyenv recommended)
- `pip install -r requirements.txt`
- Optional: set `OGC_API_KEY` (store securely; do not hard-code keys in git)

### Run Locally
```bash
git clone https://github.com/<org>/Vidyarthi-Raksha.git
cd Vidyarthi-Raksha
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### First-Time Checklist
1. In the sidebar choose 5 vans @ 150 capacity.
2. Hit **Optimize Routes** → watch spinner cursor indicate recompute.
3. Explore Strategic, Tactical, and Analytical tabs.
4. Review sample data (200 schools) generated via Digital Twin engine.

## Repository Map
```
app.py                             # Main Streamlit app
views/tab1_command.py              # Strategic Command Center
views/tab2_operations.py           # Tactical Operations
views/tab3_intelligence.py         # Analytical Intelligence
core/data_engine.py                # Digital twin generator (Phase 2)
core/optimization.py               # RouteOptimizer CVRPTW (Phase 3)
core/test_optimization.py          # Pytest suite for optimizer validation
core/validate_digital_twin.py      # Data quality validation script
data/precomputed_scenarios.py      # Real-time scenario cache (connects optimizer to UI)
requirements.txt                   # Python deps
```

## Related Repositories

| Repository | Description |
|------------|-------------|
| [Vidyarthi_raksha_models](https://github.com/ben-biju/Vidyarthi_raksha_models.git) | Data processing and analytical models for demand forecasting, risk scoring, and equity analysis |

## Core Module Reference

### `core/data_engine.py` — Digital Twin Data Generator
Generates synthetic but realistic school enrollment data for Jharkhand, India.

| Feature | Description |
|---------|-------------|
| **Schools** | N schools with realistic names, coordinates (within Jharkhand bounds), categories (70% rural / 30% urban) |
| **Enrollment Metrics** | `total_students`, `enrolled_students`, `backlog_students`, `saturation_rate` |
| **Equity Metrics** | `gender_parity_index` (GPI), `equity_risk` flag for schools with GPI < 0.90 |
| **Access Metrics** | `distance_to_center_km`, `access_risk_score` (0–100 based on distance + rural penalty) |
| **Zone Classification** | Labels schools as "Safe Zone", "Moderate Zone", or "Dark Zone" based on risk score |
| **Priority Scoring** | Combines backlog weight (60%) + equity risk (25%) + access risk (15%) |

**Key Functions:**
- `generate_digital_twin_dataset(n_schools, seed)` → Returns a DataFrame
- `get_dataset_summary(df)` → Returns summary statistics dict
- `identify_priority_clusters(df, top_n)` → Returns highest priority schools
- `ENROLLMENT_CENTERS` → List of 5 fixed Aadhaar enrollment centers in Jharkhand

---

### `core/test_optimization.py` — Route Optimizer Test Suite
Pytest-based validation that the CVRPTW route optimization algorithm works correctly.

| Test | What It Validates |
|------|-------------------|
| Basic Route Generation | Optimizer returns routes list with required fields |
| Capacity Constraints | No route exceeds `max_capacity` (150 students) |
| Time Constraints | No route exceeds `max_time_minutes` (480 min = 8 hours) |
| Vehicle Count | Number of routes ≤ requested vehicles |
| School Coverage | All schools are assigned to exactly one route |
| Route Paths | Each route has valid lat/lon path starting/ending at depot |
| Priority Scoring | Higher backlog/risk schools get higher priority scores |
| Distance Calculations | Haversine formula produces correct distances |

**Run tests:**
```bash
python -m pytest core/test_optimization.py -v
```

---

### `core/validate_digital_twin.py` — Data Quality Validation Script
Interactive script to validate and explore the generated digital twin data.

| Section | Output |
|---------|--------|
| Sample Records | First 5 schools with all fields |
| Summary Statistics | Total schools, backlog, saturation, GPI averages |
| Rural vs Urban Analysis | Comparison of metrics between categories |
| Enrollment Centers | Lists the 5 fixed Aadhaar centers |
| Top 10 Priority Schools | Highest intervention urgency schools |
| Data Distribution | Min/max/mean/std for backlog, saturation, GPI, access risk |
| Zone Breakdown | Count of Safe/Moderate/Dark Zone schools |
| Critical Insights | High-risk combinations (backlog + equity, rural + dark zone) |
| Export | Saves dataset to `data/digital_twin_schools.csv` |

**Run validation:**
```bash
python core/validate_digital_twin.py
```

---

### Data Flow Diagram
```
┌─────────────────────────────────────────────────────────────┐
│  data_engine.py                                              │
│  └─► generate_digital_twin_dataset()                        │
│           │                                                  │
│           ├──────► validate_digital_twin.py (QA & export)   │
│           │                                                  │
│           └──────► app.py (Dashboard UI)                    │
│                         │                                    │
│                         ▼                                    │
│               precomputed_scenarios.py                       │
│                    └─► ScenarioCache calls RouteOptimizer   │
│                              │                               │
│                              ▼                               │
│                      optimization.py (CVRPTW algorithm)     │
│                              │                               │
│                              ▼                               │
│                    test_optimization.py (validates algo)    │
└─────────────────────────────────────────────────────────────┘
```

## Validation & Success Metrics
- **Performance** – Initial load ≈ 8–10s, route optimization 3–5s, tab switches <1s.
- **Quality Gates** – All modules pass `python -m py_compile`; key functions typed & documented.
- **User Impact** – KPI coverage for executives, manifests for logistics, forecasts for analysts.
- **Scalability** – Cached datasets & singleton optimizers minimize reruns; responsive layout works across breakpoints.

## Documentation Index
This README is now the single source of truth. Older phase-specific markdown files were removed to keep the repository lightweight, so all operating procedures, architecture notes, and setup guidance have been consolidated here.

## Roadmap
- 🔄 Multi-depot & heterogeneous vehicle support
- 📡 Real-time GPS integration with adaptive rerouting
- 📈 ML-driven forecasting (Prophet / ARIMA)
- 📱 Field-team mobile companion & PDF manifest export
- ☁️ Streamlit Cloud or Azure App Service deployment playbook

For questions or clarifications, open an issue referencing the sections in this README. Vidyarthi-Raksha is ready for judge demos and real-world pilots alike.
