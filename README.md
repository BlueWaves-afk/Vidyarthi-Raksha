Demand-side intelligence
→ Where Aadhaar enrolment / update pressure exists and why

Supply-side capacity modeling
→ How many resources UIDAI actually has to respond (centres, kits, operators)

Actionable linkage
→ Not just “insights”, but operational decisions derived from data

OGC API KEY: 579b464db66ec23bdd000001f251a4cb0a0d44cb62aa1ed59941aff4
Our Consolidated Dataset;
A. DEMAND DATASETS
1. UIDAI Aadhaar Enrolment & Update Dataset (Core):
    -Source:
    -Derived Metrics:
    %   biometric obsolescence

        update velocity (updates/day)

        backlog growth rate

        seasonality index
2. UDISE+ School Infrastructure Dataset (Demand Amplifier):
    -Source: Ministry of Education – UDISE+ Open Data
    =Derived Metrics:
    %   expected_mbu_demand = students_age_5 + students_age_15

        school_risk_score
3. Census / Population Age Distribution (Validation Layer)
    -Source: Census of India / Sample Registration System (SRS)
    -Used to:

        Validate UIDAI age-band numbers

        Normalize outliers

        Prevent “synthetic-only” criticism

B. SUPPLY DATASETS

1. UIDAI Enrolment Centre & Kit Availability (Supply):
    -Source: UIDAI centre locator
    -Derived: daily_capacity

              effective_capacity (after downtime assumptions)

2. Mobile Aadhaar Van / Camp Data (Operational Supply):
    -Source: This is where your VRP algorithm becomes legitimate, not academic.


FINAL MASTER DATASET:
school_id
school_name
lat, lon
district
pending_mbu
risk_level
distance_to_nearest_center
nearest_center_capacity
assigned_van_id
estimated_clearance_days
priority_score

Add a Methodology section with these bullets:

✔ Data Cleaning
Removed duplicate Aadhaar enrolment records

Age-band normalization

Outlier clipping using IQR method

✔ Feature Engineering
Risk scoring using weighted backlog + distance

Demand forecasting via rolling averages

Capacity constraints modeled explicitly

✔ Reproducibility
All transformations scripted (Python/Pandas)

Deterministic random seeds for mock data

Schema-first design

✔ Ethics & Privacy
Only aggregated, anonymized UIDAI data used

No PII processed

Compliant with UIDAI data sharing norms