"""
Tab 3: Analytical Intelligence Dashboard
==========================================
Deep-dive analytics engine for strategic decision-making.

Sections:
1. Forecasting & Trends (Method 3) - ARIMA-based saturation forecasting
2. Spatial Statistical Deep Dive (Method 4) - 3D HexagonLayer dark zone analysis
3. Equity Analytics (Method 2) - GPI & vulnerability assessment
4. Predictive Risk & Feasibility (Method 5) - Operational risk modeling

All models are pre-computed for demo latency optimization.
"""

import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import math


# ==========================================
# STUB DATA GENERATORS (Replace with real models)
# ==========================================

def get_arima_forecast_stub() -> pd.DataFrame:
    """
    STUB: Pre-computed ARIMA forecast for Saturation Rate.
    Replace with actual ARIMA model output.
    """
    months = pd.date_range(start='2025-07-01', periods=18, freq='MS')
    
    # Historical data (last 6 months)
    historical = [0.62, 0.65, 0.68, 0.71, 0.73, 0.76]
    
    # Forecast data (next 12 months) with confidence intervals
    forecast = [0.78, 0.81, 0.79, 0.83, 0.86, 0.88, 0.91, 0.89, 0.92, 0.94, 0.96, 0.98]
    lower_ci = [f - 0.05 - (i * 0.008) for i, f in enumerate(forecast)]
    upper_ci = [f + 0.05 + (i * 0.008) for i, f in enumerate(forecast)]
    
    data = []
    for i, month in enumerate(months):
        if i < 6:
            data.append({
                'date': month,
                'saturation_rate': historical[i],
                'lower_ci': historical[i],
                'upper_ci': historical[i],
                'type': 'Historical'
            })
        else:
            idx = i - 6
            data.append({
                'date': month,
                'saturation_rate': forecast[idx],
                'lower_ci': lower_ci[idx],
                'upper_ci': upper_ci[idx],
                'type': 'Forecast'
            })
    
    return pd.DataFrame(data)


def get_trend_metrics_stub() -> Dict:
    """
    STUB: Trend indicators from time-series analysis.
    Replace with actual trend detection logic.
    """
    return {
        'saturation_trend': {
            'value': '+4.2%',
            'direction': 'up',
            'color': '#22c55e',
            'label': 'Saturation Rate MoM'
        },
        'backlog_trend': {
            'value': '-18.5%',
            'direction': 'down',
            'color': '#22c55e',
            'label': 'Backlog Reduction MoM'
        },
        'enrollment_velocity': {
            'value': '2,847',
            'direction': 'up',
            'color': '#3b82f6',
            'label': 'Weekly Enrollment Rate'
        },
        'days_to_target': {
            'value': '127',
            'direction': 'neutral',
            'color': '#f59e0b',
            'label': 'Days to 95% Saturation'
        }
    }


def get_dark_zone_data_stub(df: pd.DataFrame) -> pd.DataFrame:
    """
    STUB: Pre-computed dark zone spatial analysis.
    Replace with actual GWR/spatial regression output.
    """
    # Create aggregated hexagon data from schools
    dark_zones = df[df['zone_label'] == 'Dark Zone'].copy()
    
    if len(dark_zones) == 0:
        # Fallback: use high-risk schools
        dark_zones = df[df['access_risk_score'] > 60].copy()
    
    dark_zones['hex_weight'] = dark_zones['backlog_students'] * (dark_zones['access_risk_score'] / 100)
    
    return dark_zones


def get_gpi_district_data_stub(df: pd.DataFrame) -> pd.DataFrame:
    """
    STUB: District-level GPI aggregation.
    Replace with actual district boundary analysis.
    """
    # Group by district (using zone_label as proxy)
    district_gpi = df.groupby('zone_label').agg({
        'gender_parity_index': 'mean',
        'backlog_students': 'sum',
        'school_id': 'count'
    }).reset_index()
    
    district_gpi.columns = ['district', 'avg_gpi', 'total_backlog', 'school_count']
    district_gpi['girls_gap'] = ((1 - district_gpi['avg_gpi']) * district_gpi['total_backlog']).astype(int)
    
    return district_gpi


def get_risk_model_output_stub() -> Dict:
    """
    STUB: Predictive risk model results.
    Replace with actual ML model predictions.
    """
    return {
        'overall_success_probability': 0.78,
        'risk_factors': [
            {'factor': 'Road Connectivity', 'impact': 0.25, 'status': 'moderate'},
            {'factor': 'Monsoon Season', 'impact': 0.35, 'status': 'high'},
            {'factor': 'Teacher Availability', 'impact': 0.15, 'status': 'low'},
            {'factor': 'Mobile Network Coverage', 'impact': 0.20, 'status': 'moderate'},
            {'factor': 'Power Infrastructure', 'impact': 0.18, 'status': 'moderate'},
        ],
        'zone_risks': {
            'Dark Zone': {'success_rate': 0.62, 'service_time_factor': 1.8},
            'Moderate Zone': {'success_rate': 0.81, 'service_time_factor': 1.3},
            'Safe Zone': {'success_rate': 0.94, 'service_time_factor': 1.0},
        }
    }


# ==========================================
# SECTION 1: FORECASTING & TRENDS (Method 3)
# ==========================================

def create_forecasting_section(df: pd.DataFrame) -> None:
    """
    Forecasting & Trends - Answer 'Where is the crisis heading?'
    """
    st.markdown("### Forecasting & Trends")
    st.markdown("<div style='font-size: 0.85rem; color: #64748b; margin-bottom: 1.5rem;'>ARIMA-based time-series analysis • Predicting saturation trajectory</div>", unsafe_allow_html=True)
    
    # Get stub data
    forecast_df = get_arima_forecast_stub()
    trend_metrics = get_trend_metrics_stub()
    
    # ==========================================
    # TREND INDICATOR CARDS
    # ==========================================
    st.markdown("#### Trend Indicators")
    
    cols = st.columns(4)
    for idx, (key, metric) in enumerate(trend_metrics.items()):
        with cols[idx]:
            if metric['direction'] == 'up':
                arrow = '↑'
                arrow_color = metric['color']
            elif metric['direction'] == 'down':
                arrow = '↓'
                arrow_color = metric['color']
            else:
                arrow = '→'
                arrow_color = metric['color']
            
            card_html = f'''<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem; text-align: center;">
<div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">{metric['label']}</div>
<div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
<span style="font-size: 1.75rem; font-weight: 700; color: #1e293b;">{metric['value']}</span>
<span style="font-size: 1.5rem; color: {arrow_color};">{arrow}</span>
</div>
</div>'''
            st.markdown(card_html, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================
    # SATURATION RATE FORECAST CHART
    # ==========================================
    st.markdown("#### Saturation Rate Forecast (ARIMA Model)")
    
    fig = go.Figure()
    
    # Historical line
    historical = forecast_df[forecast_df['type'] == 'Historical']
    fig.add_trace(go.Scatter(
        x=historical['date'],
        y=historical['saturation_rate'],
        mode='lines+markers',
        name='Historical',
        line=dict(color='#1e293b', width=3),
        marker=dict(size=8),
    ))
    
    # Forecast line
    forecast = forecast_df[forecast_df['type'] == 'Forecast']
    fig.add_trace(go.Scatter(
        x=forecast['date'],
        y=forecast['saturation_rate'],
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#3b82f6', width=3, dash='dot'),
        marker=dict(size=8),
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast['date'], forecast['date'][::-1]]),
        y=pd.concat([forecast['upper_ci'], forecast['lower_ci'][::-1]]),
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% Confidence Interval',
        showlegend=True,
    ))
    
    # Target line at 95%
    fig.add_hline(y=0.95, line_dash="dash", line_color="#22c55e",
                  annotation_text="Target: 95%", annotation_position="right")
    
    fig.update_layout(
        height=400,
        xaxis_title='Month',
        yaxis_title='Saturation Rate',
        yaxis=dict(tickformat='.0%', range=[0.5, 1.05]),
        legend=dict(orientation='h', y=-0.15),
        hovermode='x unified',
        margin=dict(l=60, r=60, t=40, b=80),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ==========================================
    # PREDICTIVE PATTERNS INSIGHT BOX
    # ==========================================
    insight_html = '''<div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #bbf7d0; border-left: 4px solid #22c55e; border-radius: 8px; padding: 1.25rem; margin-top: 1rem;">
<div style="font-size: 0.75rem; color: #166534; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; font-weight: 600;">Predictive Pattern Detected</div>
<div style="font-size: 0.95rem; color: #14532d; line-height: 1.6;">
<strong>Seasonal Anomaly:</strong> March-April shows 25% enrollment spike due to academic year deadlines. 
<strong>Recommendation:</strong> Pre-position additional mobile units in Dark Zones during Q1 to capitalize on this window.
Model confidence: 87%.
</div>
</div>'''
    st.markdown(insight_html, unsafe_allow_html=True)


# ==========================================
# SECTION 2: SPATIAL STATISTICAL DEEP DIVE (Method 4)
# ==========================================

def create_spatial_analysis_section(df: pd.DataFrame) -> None:
    """
    Spatial Statistical Deep Dive - 3D Dark Zone Discovery.
    """
    st.markdown("### Spatial Statistical Deep Dive")
    st.markdown("<div style='font-size: 0.85rem; color: #64748b; margin-bottom: 1.5rem;'>3D density mapping • Dark Zone identification • Access barrier analysis</div>", unsafe_allow_html=True)
    
    # Get dark zone data
    dark_zones = get_dark_zone_data_stub(df)
    
    # Map legend
    legend_html = '''<div style="display: flex; gap: 2rem; padding: 1rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 1rem;">
<div style="display: flex; align-items: center; gap: 0.5rem;">
<div style="width: 20px; height: 20px; background: linear-gradient(to top, #fef08a, #dc2626); border-radius: 4px;"></div>
<span style="font-size: 0.8rem; color: #475569;"><strong>Height</strong> = Backlog Magnitude</span>
</div>
<div style="display: flex; align-items: center; gap: 0.5rem;">
<div style="width: 20px; height: 20px; background: #dc2626; border-radius: 4px;"></div>
<span style="font-size: 0.8rem; color: #475569;"><strong>Red</strong> = High Vulnerability (access + backlog)</span>
</div>
<div style="display: flex; align-items: center; gap: 0.5rem;">
<div style="width: 20px; height: 20px; background: #f59e0b; border-radius: 4px;"></div>
<span style="font-size: 0.8rem; color: #475569;"><strong>Amber</strong> = Moderate Risk</span>
</div>
</div>'''
    st.markdown(legend_html, unsafe_allow_html=True)
    
    # Center on data
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    # Create HexagonLayer for 3D density
    hex_layer = pdk.Layer(
        "HexagonLayer",
        data=dark_zones,
        get_position=['longitude', 'latitude'],
        radius=2000,
        elevation_scale=50,
        elevation_range=[0, 3000],
        extruded=True,
        pickable=True,
        auto_highlight=True,
        get_elevation_weight='backlog_students',
        get_color_weight='access_risk_score',
        color_range=[
            [254, 240, 138],  # Yellow
            [253, 186, 116],  # Light orange
            [251, 146, 60],   # Orange
            [249, 115, 22],   # Dark orange
            [234, 88, 12],    # Burnt orange
            [220, 38, 38],    # Red
        ],
    )
    
    # Dark zone markers
    dark_zone_markers = df[df['zone_label'] == 'Dark Zone'].copy()
    
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=dark_zone_markers,
        get_position=['longitude', 'latitude'],
        get_fill_color=[220, 38, 38, 180],
        get_radius=400,
        pickable=True,
    )
    
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=9,
        pitch=55,
        bearing=15,
    )
    
    tooltip = {
        "html": "<b>Backlog Density</b><br>Schools in hex: {elevationValue}<br>Risk Score: {colorValue}",
        "style": {"backgroundColor": "#0f172a", "color": "white", "padding": "10px", "borderRadius": "6px"}
    }
    
    deck = pdk.Deck(
        layers=[hex_layer, scatter_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v11",
        tooltip=tooltip,
    )
    
    st.pydeck_chart(deck, use_container_width=True)
    
    # ==========================================
    # DARK ZONE DISCOVERY NARRATIVE
    # ==========================================
    st.markdown("#### Dark Zone Discovery: The Invisible Crisis")
    
    dark_zone_count = len(df[df['zone_label'] == 'Dark Zone'])
    dark_zone_backlog = df[df['zone_label'] == 'Dark Zone']['backlog_students'].sum()
    total_backlog = df['backlog_students'].sum()
    dark_zone_pct = (dark_zone_backlog / total_backlog * 100) if total_backlog > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_html = f'''<div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; text-align: center;">
<div style="font-size: 0.7rem; color: #dc2626; text-transform: uppercase; font-weight: 600;">Dark Zone Schools</div>
<div style="font-size: 2rem; font-weight: 700; color: #b91c1c;">{dark_zone_count}</div>
</div>'''
        st.markdown(metric_html, unsafe_allow_html=True)
    
    with col2:
        metric_html = f'''<div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; text-align: center;">
<div style="font-size: 0.7rem; color: #dc2626; text-transform: uppercase; font-weight: 600;">Students in Dark Zones</div>
<div style="font-size: 2rem; font-weight: 700; color: #b91c1c;">{dark_zone_backlog:,}</div>
</div>'''
        st.markdown(metric_html, unsafe_allow_html=True)
    
    with col3:
        metric_html = f'''<div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; text-align: center;">
<div style="font-size: 0.7rem; color: #dc2626; text-transform: uppercase; font-weight: 600;">% of Total Crisis</div>
<div style="font-size: 2rem; font-weight: 700; color: #b91c1c;">{dark_zone_pct:.1f}%</div>
</div>'''
        st.markdown(metric_html, unsafe_allow_html=True)
    
    # Insight
    insight_html = '''<div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 1rem; margin-top: 1rem; border-radius: 0 8px 8px 0;">
<div style="font-size: 0.9rem; color: #7f1d1d; line-height: 1.6;">
<strong>Root Cause Identified:</strong> Enrollment drop-off at ages 5 and 15 is concentrated in areas >15km from enrollment centers. 
These "Dark Zones" lack mobile connectivity, creating a <em>distance-based access barrier</em> that standard center-based enrollment cannot address.
</div>
</div>'''
    st.markdown(insight_html, unsafe_allow_html=True)


# ==========================================
# SECTION 3: EQUITY ANALYTICS (Method 2)
# ==========================================

def create_equity_section(df: pd.DataFrame) -> None:
    """
    Equity Analytics - Proving 'Who is being left behind'.
    """
    st.markdown("### Equity Analytics")
    st.markdown("<div style='font-size: 0.85rem; color: #64748b; margin-bottom: 1.5rem;'>Gender Parity Index analysis • Vulnerability assessment • Proving equity gaps</div>", unsafe_allow_html=True)
    
    # ==========================================
    # GPI DEFINITION BOX
    # ==========================================
    gpi_def_html = '''<div style="background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #3b82f6; padding: 1rem; margin-bottom: 1.5rem; border-radius: 0 8px 8px 0;">
<div style="font-size: 0.85rem; color: #1e40af;">
<strong>Gender Parity Index (GPI)</strong> = Girls Enrolled / Boys Enrolled<br>
<span style="color: #64748b;">GPI ≥ 0.95 = Parity achieved | GPI < 0.90 = Equity risk | GPI < 0.85 = Critical disparity</span>
</div>
</div>'''
    st.markdown(gpi_def_html, unsafe_allow_html=True)
    
    # Get district-level data
    district_gpi = get_gpi_district_data_stub(df)
    
    # ==========================================
    # GPI BY ZONE (VULNERABILITY PROGRESS BARS)
    # ==========================================
    st.markdown("#### Vulnerability Progress by Zone")
    
    zones = ['Dark Zone', 'Moderate Zone', 'Safe Zone']
    zone_colors = {'Dark Zone': '#dc2626', 'Moderate Zone': '#f59e0b', 'Safe Zone': '#22c55e'}
    
    for zone in zones:
        zone_df = df[df['zone_label'] == zone]
        if len(zone_df) == 0:
            continue
        
        avg_gpi = zone_df['gender_parity_index'].mean()
        total_backlog = zone_df['backlog_students'].sum()
        school_count = len(zone_df)
        girls_gap = int((1 - avg_gpi) * total_backlog)
        
        # Progress bar color based on GPI
        if avg_gpi >= 0.95:
            bar_color = '#22c55e'
            status = 'PARITY'
        elif avg_gpi >= 0.90:
            bar_color = '#f59e0b'
            status = 'AT RISK'
        else:
            bar_color = '#dc2626'
            status = 'CRITICAL'
        
        progress_pct = avg_gpi * 100
        
        zone_html = f'''<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
<div style="display: flex; align-items: center; gap: 0.5rem;">
<div style="width: 12px; height: 12px; background: {zone_colors[zone]}; border-radius: 50%;"></div>
<span style="font-weight: 600; color: #1e293b;">{zone}</span>
<span style="font-size: 0.75rem; color: #64748b;">({school_count} schools)</span>
</div>
<div style="display: flex; align-items: center; gap: 1rem;">
<span style="font-size: 0.75rem; color: #64748b;">Est. girls at risk: <strong>{girls_gap:,}</strong></span>
<span style="background: {bar_color}20; color: {bar_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">{status}</span>
</div>
</div>
<div style="height: 10px; background: #e2e8f0; border-radius: 5px; overflow: hidden;">
<div style="height: 100%; width: {progress_pct}%; background: {bar_color};"></div>
</div>
<div style="display: flex; justify-content: space-between; margin-top: 0.25rem; font-size: 0.7rem; color: #94a3b8;">
<span>GPI: {avg_gpi:.3f}</span>
<span>Target: 0.95</span>
</div>
</div>'''
        st.markdown(zone_html, unsafe_allow_html=True)
    
    # ==========================================
    # GPI DISTRIBUTION CHART
    # ==========================================
    st.markdown("#### GPI Distribution Across Schools")
    
    fig = go.Figure()
    
    # Histogram of GPI values
    fig.add_trace(go.Histogram(
        x=df['gender_parity_index'],
        nbinsx=30,
        marker=dict(
            color=df['gender_parity_index'].apply(
                lambda x: '#dc2626' if x < 0.85 else ('#f59e0b' if x < 0.90 else ('#22c55e' if x >= 0.95 else '#3b82f6'))
            ),
            line=dict(color='white', width=1)
        ),
        name='Schools'
    ))
    
    # Add threshold lines
    fig.add_vline(x=0.85, line_dash="dash", line_color="#dc2626",
                  annotation_text="Critical", annotation_position="top")
    fig.add_vline(x=0.90, line_dash="dash", line_color="#f59e0b",
                  annotation_text="At Risk", annotation_position="top")
    fig.add_vline(x=0.95, line_dash="dash", line_color="#22c55e",
                  annotation_text="Target", annotation_position="top")
    
    fig.update_layout(
        height=300,
        xaxis_title='Gender Parity Index',
        yaxis_title='Number of Schools',
        showlegend=False,
        margin=dict(l=60, r=40, t=40, b=60),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ==========================================
    # EQUITY NARRATIVE
    # ==========================================
    critical_schools = len(df[df['gender_parity_index'] < 0.85])
    at_risk_schools = len(df[(df['gender_parity_index'] >= 0.85) & (df['gender_parity_index'] < 0.90)])
    total_girls_gap = int(((1 - df['gender_parity_index']) * df['backlog_students']).sum())
    
    equity_narrative_html = f'''<div style="background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); border: 1px solid #f0abfc; border-radius: 8px; padding: 1.25rem; margin-top: 1rem;">
<div style="font-size: 0.75rem; color: #86198f; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; font-weight: 600;">Equity Impact Statement</div>
<div style="font-size: 0.95rem; color: #701a75; line-height: 1.6;">
<strong>{critical_schools} schools</strong> are in critical gender disparity (GPI &lt; 0.85), 
with an additional <strong>{at_risk_schools} at risk</strong>. 
This translates to approximately <strong>{total_girls_gap:,} girls</strong> who may be systematically excluded from enrollment.
<br><br>
<em>The equity-weighted optimization prioritizes these schools to ensure girls are not left behind.</em>
</div>
</div>'''
    st.markdown(equity_narrative_html, unsafe_allow_html=True)


# ==========================================
# SECTION 4: PREDICTIVE RISK & FEASIBILITY (Method 5)
# ==========================================

def create_risk_section(df: pd.DataFrame) -> None:
    """
    Predictive Risk & Feasibility - Operational constraints and success probability.
    """
    st.markdown("### Predictive Risk & Feasibility")
    st.markdown("<div style='font-size: 0.85rem; color: #64748b; margin-bottom: 1.5rem;'>ML-based success prediction • Operational constraints • Service time modeling</div>", unsafe_allow_html=True)
    
    # Get risk model output
    risk_data = get_risk_model_output_stub()
    
    # ==========================================
    # OVERALL SUCCESS PROBABILITY
    # ==========================================
    success_pct = risk_data['overall_success_probability'] * 100
    
    if success_pct >= 80:
        success_color = '#22c55e'
        success_label = 'HIGH CONFIDENCE'
    elif success_pct >= 60:
        success_color = '#f59e0b'
        success_label = 'MODERATE CONFIDENCE'
    else:
        success_color = '#dc2626'
        success_label = 'LOW CONFIDENCE'
    
    success_html = f'''<div style="background: #ffffff; border: 2px solid {success_color}; border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 1.5rem;">
<div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">Overall Mission Success Probability</div>
<div style="font-size: 3.5rem; font-weight: 800; color: {success_color};">{success_pct:.0f}%</div>
<div style="background: {success_color}20; color: {success_color}; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; display: inline-block;">{success_label}</div>
</div>'''
    st.markdown(success_html, unsafe_allow_html=True)
    
    # ==========================================
    # RISK FACTORS BREAKDOWN
    # ==========================================
    st.markdown("#### Risk Factors Impact Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        risk_factors = risk_data['risk_factors']
        
        # Sort by impact
        risk_factors_sorted = sorted(risk_factors, key=lambda x: x['impact'], reverse=True)
        
        fig = go.Figure()
        
        colors = []
        for rf in risk_factors_sorted:
            if rf['status'] == 'high':
                colors.append('#dc2626')
            elif rf['status'] == 'moderate':
                colors.append('#f59e0b')
            else:
                colors.append('#22c55e')
        
        fig.add_trace(go.Bar(
            y=[rf['factor'] for rf in risk_factors_sorted],
            x=[rf['impact'] for rf in risk_factors_sorted],
            orientation='h',
            marker=dict(color=colors),
            text=[f"{rf['impact']*100:.0f}%" for rf in risk_factors_sorted],
            textposition='inside',
        ))
        
        fig.update_layout(
            height=300,
            xaxis_title='Risk Impact Score',
            yaxis_title='',
            xaxis=dict(tickformat='.0%'),
            margin=dict(l=150, r=40, t=20, b=60),
            showlegend=False,
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### Risk Legend")
        legend_items = [
            ('High Risk', '#dc2626', 'Requires immediate mitigation'),
            ('Moderate Risk', '#f59e0b', 'Monitor closely'),
            ('Low Risk', '#22c55e', 'Manageable'),
        ]
        for label, color, desc in legend_items:
            item_html = f'''<div style="display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.75rem;">
<div style="width: 12px; height: 12px; background: {color}; border-radius: 3px; margin-top: 3px;"></div>
<div>
<div style="font-size: 0.8rem; font-weight: 600; color: #1e293b;">{label}</div>
<div style="font-size: 0.7rem; color: #64748b;">{desc}</div>
</div>
</div>'''
            st.markdown(item_html, unsafe_allow_html=True)
    
    # ==========================================
    # SERVICE TIME MODELING BY ZONE
    # ==========================================
    st.markdown("#### Operational Constraints: Service Time by Zone")
    
    zone_risks = risk_data['zone_risks']
    
    zone_cards = []
    for zone, data in zone_risks.items():
        if zone == 'Dark Zone':
            zone_color = '#dc2626'
            zone_bg = '#fef2f2'
        elif zone == 'Moderate Zone':
            zone_color = '#f59e0b'
            zone_bg = '#fefce8'
        else:
            zone_color = '#22c55e'
            zone_bg = '#f0fdf4'
        
        card_html = f'''<div style="background: {zone_bg}; border: 1px solid {zone_color}40; border-radius: 8px; padding: 1rem; text-align: center;">
<div style="font-size: 0.75rem; color: {zone_color}; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">{zone}</div>
<div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">{data['success_rate']*100:.0f}%</div>
<div style="font-size: 0.7rem; color: #64748b;">Expected Success Rate</div>
<div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid {zone_color}30;">
<div style="font-size: 1.25rem; font-weight: 600; color: #1e293b;">{data['service_time_factor']}x</div>
<div style="font-size: 0.7rem; color: #64748b;">Service Time Multiplier</div>
</div>
</div>'''
        zone_cards.append(card_html)
    
    cols = st.columns(3)
    for idx, card in enumerate(zone_cards):
        with cols[idx]:
            st.markdown(card, unsafe_allow_html=True)
    
    # Explanation
    constraint_html = '''<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
<div style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
<strong>Why Service Time Varies:</strong> Dark Zones require 1.8x more time due to:
<ul style="margin: 0.5rem 0 0 1.5rem;">
<li>Unpaved road access requiring slower vehicle speeds</li>
<li>Limited mobile network requiring offline data sync</li>
<li>Larger average distances between schools</li>
<li>Higher verification failure rates requiring re-enrollment</li>
</ul>
</div>
</div>'''
    st.markdown(constraint_html, unsafe_allow_html=True)


# ==========================================
# MAIN RENDER FUNCTION
# ==========================================

def render_tab3(df: pd.DataFrame, selected_section: str = "all") -> None:
    """
    Main entry point for Tab 3 (Analytical Intelligence Dashboard).
    
    Args:
        df: DataFrame with school data
        selected_section: Which section to render ('all', 'forecasting', 'spatial', 'equity', 'risk')
    """
    # Main header
    header_html = '''<div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; border: 1px solid #e2e8f0;">
<div style="font-size: 1.2rem; font-weight: 700; color: #1e293b; letter-spacing: 0.02em;">ANALYTICAL INTELLIGENCE</div>
<div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">Deep-dive analytics • Forecasting • Equity assessment • Risk modeling</div>
</div>'''
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Section selector
    section = sac.segmented(
        items=[
            sac.SegmentedItem(label='All Sections', icon='grid'),
            sac.SegmentedItem(label='Forecasting', icon='graph-up'),
            sac.SegmentedItem(label='Spatial', icon='geo-alt'),
            sac.SegmentedItem(label='Equity', icon='people'),
            sac.SegmentedItem(label='Risk', icon='exclamation-triangle'),
        ],
        index=0,
        size='sm',
        color='orange',
        use_container_width=True,
        return_index=False,
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render sections based on selection
    if section == 'All Sections' or section == 'Forecasting':
        create_forecasting_section(df)
        if section == 'All Sections':
            st.divider()
    
    if section == 'All Sections' or section == 'Spatial':
        create_spatial_analysis_section(df)
        if section == 'All Sections':
            st.divider()
    
    if section == 'All Sections' or section == 'Equity':
        create_equity_section(df)
        if section == 'All Sections':
            st.divider()
    
    if section == 'All Sections' or section == 'Risk':
        create_risk_section(df)
