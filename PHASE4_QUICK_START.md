# Phase 4: Quick Start Guide

## Running the Dashboard

### Option 1: New Integrated Dashboard (Recommended)
```bash
cd /Users/tommathew/Documents/Vidyarthi-Raksha
streamlit run app_phase4.py
```

This launches the **complete Phase 4 dashboard** with all three tabs:
- **Strategic** (Tab 1): KPIs, hexagon map, zone breakdown
- **Tactical** (Tab 2): Route visualization, Gantt schedule
- **Analytical** (Tab 3): Forecasting, GPI analysis

### Option 2: Original Dashboard (Legacy)
```bash
streamlit run app.py
```

---

## Using the Dashboard

### Sidebar: Scenario Planning

1. **Number of Mobile Units**: Adjust 1-10 vehicles
   - More vehicles → Lower utilization but faster completion
   - Fewer vehicles → Higher utilization but longer timeline

2. **Daily Capacity**: Adjust 50-500 students/day per unit
   - Higher capacity → Fewer vehicles needed
   - Lower capacity → More focused visits

3. **Priority Weighting**: Adjust Backlog vs Access Risk
   - 70% Backlog / 30% Access: Default (students first)
   - 100% Backlog / 0% Access: Maximize enrollments
   - 0% Backlog / 100% Access: Maximize reach

4. **Click "🚀 Optimize Routes"** to generate vehicle routes
   - Optimization takes 3-5 seconds
   - Routes appear in Tab 2 immediately

### Tab 1: Strategic Command Center

**What to look for:**
- ✅ Is Total Backlog manageable? (~4,000-5,000 students)
- ✅ Are Dark Zones concentrated? (If yes, prioritize them)
- ✅ Is GPI below 0.9? (Equity alerts need attention)
- ✅ What % of schools are rural? (Rural penalty = lower saturation)

**Actions:**
- Identify Dark Zones on the hexagon map
- Note schools with worst equity metrics
- Plan targeted interventions

### Tab 2: Tactical Operations

**What to look for:**
- ✅ Do routes cover all critical schools?
- ✅ Are vehicles balanced in load?
- ✅ Any vehicle over 95% capacity?
- ✅ Coverage % of backlog acceptable?

**Actions:**
- Adjust vehicle count if imbalanced
- Re-optimize if coverage <80%
- Export manifests for field deployment

### Tab 3: Analytical Intelligence

**What to look for:**
- ✅ Will backlog clear within 12 months?
- ✅ Which schools have worst gender parity?
- ✅ Are rural schools significantly behind?

**Actions:**
- Plan intensive campaigns for critical GPI schools
- Consider rural-specific interventions
- Adjust forecast assumptions if needed

---

## Key Metrics Explained

### KPI Cards (Tab 1)

**Total Backlog**: Sum of unenrolled 15-year-old cohort
- Formula: Sum(backlog_students)
- Target: Reduce to zero within 12 months
- Action: Adjust vehicle count if timeline too long

**Avg Saturation**: Percentage of eligible students already enrolled
- Formula: Mean(saturation_rate) × 100
- Target: >80%
- Rural Penalty: -15% for schools >25km from depot

**Dark Zones**: Schools with high access barriers
- Definition: Schools in "Dark Zone" classification
- Cause: Distance >25km AND saturation <50%
- Action: Priority for mobile units

**Equity Alerts**: Schools with gender disparity
- Definition: Gender Parity Index <0.9
- Cause: Fewer girls than boys enrolled
- Action: Targeted awareness campaigns

### Route Metrics (Tab 2)

**Capacity Utilization**
- Formula: (total_students / max_capacity) × 100
- Ideal: 80-95%
- <60%: Vehicle underutilized
- >95%: Vehicle overutilized

**Time Utilization**
- Formula: (total_time_minutes / max_time_minutes) × 100
- Ideal: 80-90%
- <60%: Extra time available
- >90%: Risk of schedule slippage

**Coverage %**
- Formula: (backlog_covered / total_backlog) × 100
- Target: 100% in first round
- Fallback: 80% acceptable if resource constraints

### Forecast Metrics (Tab 3)

**Backlog Reduction Rate**
- Default: 18% per month (600 students/month)
- Seasonal spike: Up to 22% in March-April
- Summer dip: Down to 17% in June-July

**GPI Thresholds**
- 🟢 ≥0.95: Excellent (target)
- 🟡 0.90-0.95: Good
- 🟠 0.85-0.90: At risk
- 🔴 <0.85: Critical

---

## Troubleshooting

### "No routes available" message in Tab 2
- **Cause**: Haven't clicked "Optimize Routes" yet
- **Fix**: Use sidebar to configure fleet, then click button

### Hexagon map not showing in Tab 1
- **Cause**: Mapbox connection issue
- **Fix**: Check internet connection, refresh page
- **Fallback**: Map uses open-street-map (should always work)

### Gantt chart looks flat in Tab 2
- **Cause**: All routes have similar duration
- **Fix**: This is normal - visit times are uniform (30 min/school)
- **Expected**: Chart shows schedule, not duration variation

### Routes seem unbalanced (e.g., VAN-001 has 20 schools, VAN-002 has 3)
- **Cause**: KMeans clustering created unequal clusters
- **Fix**: Adjust vehicle count and re-optimize
- **Note**: Greedy algorithm prioritizes backlog, not perfect balance

### App loads slowly
- **Cause**: Streamlit rerunning entire script
- **Fix**: Normal behavior on first load; subsequent loads cached
- **Optimization**: PyDeck map rendering can be slow on large datasets

### GPI chart shows "Diverging Bar" but not diverging
- **Cause**: GPI values very close together
- **Fix**: This is good! Schools have similar gender parity
- **Action**: Focus on remaining outliers

---

## Tips & Best Practices

### Planning Routes
1. **Start with 3 vehicles**: Baseline fleet size
2. **Monitor coverage %**: Aim for >95%
3. **Check capacity utilization**: Ideal is 85-90%
4. **Verify time windows**: Ensure realistic schedule

### Optimizing for Equity
1. **Check Tab 1 zone breakdown**: Where are disparities?
2. **Review Tab 3 GPI analysis**: Which schools need focus?
3. **Look at Tab 2 coverage**: Are equity schools included?
4. **Adjust weights**: Increase "Access Risk Weight" if rural underserved

### Forecasting
1. **Monitor Tab 3 forecast**: Is backlog on track?
2. **Adjust assumptions**: Weather, holidays, emergencies
3. **Plan interventions**: Intensive campaigns in spike months
4. **Review historical data**: Compare forecast to actuals

### Field Deployment
1. **Export routes from Tab 2**: Use "Download" buttons
2. **Share manifests with drivers**: School list, sequence, timing
3. **Update Tab 2 after each day**: Re-optimize based on completions
4. **Monitor Tab 3 forecast**: Adjust if pace differs

---

## Sample Scenarios

### Scenario 1: Maximum Speed (Minimize Time)
```
Setting:
- Number of Vehicles: 8
- Daily Capacity: 200 students/day
- Backlog Weight: 100%
- Access Risk Weight: 0%

Expected Result:
- Est. Days to Clear: ~3 weeks
- Backlog Coverage: 100%
- Capacity Utilization: 85%
- Trade-off: May miss some low-access schools
```

### Scenario 2: Balanced Approach (Default)
```
Setting:
- Number of Vehicles: 3
- Daily Capacity: 150 students/day
- Backlog Weight: 70%
- Access Risk Weight: 30%

Expected Result:
- Est. Days to Clear: ~8-10 weeks
- Backlog Coverage: 87%
- Capacity Utilization: 92%
- Trade-off: Good balance between speed & equity
```

### Scenario 3: Equity-First (Minimize Disparity)
```
Setting:
- Number of Vehicles: 5
- Daily Capacity: 120 students/day
- Backlog Weight: 30%
- Access Risk Weight: 70%

Expected Result:
- Est. Days to Clear: ~12 weeks
- Backlog Coverage: 75%
- Capacity Utilization: 78%
- Trade-off: Reaches hard-to-access schools first
```

---

## File Locations

| File | Purpose | Size |
|------|---------|------|
| `app_phase4.py` | Main dashboard (NEW) | ~450 lines |
| `views/tab1_command.py` | Strategic tab | ~346 lines |
| `views/tab2_operations.py` | Tactical tab | ~338 lines |
| `views/tab3_intelligence.py` | Analytical tab | ~344 lines |
| `core/data_engine.py` | Data generation | 500+ lines |
| `core/optimization.py` | Route solver | 750+ lines |
| `PHASE4_INTERFACE_DOCUMENTATION.md` | Full reference | This file |

---

## Next Steps (Phase 5)

- [ ] Real-time GPS tracking for vehicles
- [ ] Integration with DISHA national database
- [ ] Mobile app for field staff
- [ ] Advanced forecasting (ML-based)
- [ ] PDF reporting with maps
- [ ] SMS alerts for critical situations

---

**Need help?** Check the documentation files or contact the project team.

**Last Updated**: January 18, 2026
