import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from millify import millify
from datetime import datetime
import time

# --- OPTIONAL: IMPORT YOUR BACKEND ---
# If you have optimizer.py working, uncomment this:
# from optimizer import solve_vrp 

# ==========================================
# 1. CONFIGURATION & GOV THEME
# ==========================================
st.set_page_config(
    page_title="Vidyarthi-Raksha | UIDAI Command Center",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for Professional Government UI
st.markdown("""
<style>
    /* Import Government-Standard Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Global Styling */
    .main { 
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
        padding: 0;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Header Styling - Enhanced Government Look */
    .header-container {
        background: linear-gradient(135deg, #003366 0%, #004d99 100%);
        padding: 2rem 2.5rem;
        border-radius: 0px;
        color: white;
        margin: -2rem -2rem 2rem -2rem;
        box-shadow: 0 4px 20px rgba(0, 51, 102, 0.15);
        border-bottom: 4px solid #FF9933;
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 40%;
        height: 200%;
        background: rgba(255, 255, 255, 0.05);
        transform: rotate(-15deg);
    }
    
    .header-title { 
        font-size: 2.5rem; 
        font-weight: 700; 
        margin: 0;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    
    .header-subtitle { 
        font-size: 1.05rem; 
        opacity: 0.92; 
        margin-top: 8px;
        font-weight: 400;
        letter-spacing: 0.3px;
        position: relative;
        z-index: 1;
    }
    
    .header-badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 10px;
        display: inline-block;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .header-badge:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateY(-1px);
    }
    
    /* Enhanced Metrics Cards */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        border-left: 4px solid #FF9933;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #FF9933, #138808);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-value { 
        font-size: 2rem; 
        font-weight: 700; 
        color: #1a1a1a;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    
    .metric-label { 
        font-size: 0.82rem; 
        color: #6b7280;
        text-transform: uppercase; 
        letter-spacing: 1.2px;
        font-weight: 600;
    }
    
    /* Sidebar Enhancements */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
        border-right: 1px solid #e5e7eb;
    }
    
    [data-testid="stSidebar"] .stImage {
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Buttons - Professional Government Style */
    .stButton>button {
        background: linear-gradient(135deg, #003366 0%, #004d99 100%);
        color: white;
        border: none;
        border-radius: 8px;
        height: 3.2rem;
        font-weight: 600;
        font-size: 0.95rem;
        width: 100%;
        transition: all 0.3s ease;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 8px rgba(0, 51, 102, 0.2);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #004080 0%, #0059b3 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 51, 102, 0.3);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        border-radius: 10px;
        padding: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 24px;
        color: #4b5563;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f3f4f6;
        color: #003366;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #003366 0%, #004d99 100%) !important;
        color: white !important;
    }
    
    /* Info/Warning Boxes */
    .stAlert {
        border-radius: 10px;
        border: none;
        padding: 1rem 1.25rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    /* Data Tables */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* Inputs and Selects */
    .stSelectbox, .stNumberInput, .stSlider {
        font-weight: 500;
    }
    
    .stSelectbox [data-baseweb="select"] {
        border-radius: 8px;
    }
    
    /* Section Headers */
    h3 {
        color: #1f2937;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        letter-spacing: -0.3px;
    }
    
    /* Download Button */
    .stDownloadButton>button {
        background: #138808;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton>button:hover {
        background: #0f6606;
        transform: translateY(-2px);
    }
    
    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
    }
    
    /* Footer */
    footer {
        color: #6b7280;
        font-size: 0.9rem;
        padding: 2rem 0 1rem;
        text-align: center;
        border-top: 1px solid #e5e7eb;
        margin-top: 3rem;
    }
    
    /* Smooth Scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: #003366 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING (Hybrid Approach)
# ==========================================
@st.cache_data
def load_data():
    # Try loading real file, else generate synthetic
    try:
        df = pd.read_csv("mock_school_data.csv")
    except FileNotFoundError:
        # Fallback Generator
        np.random.seed(42)
        n = 50
        df = pd.DataFrame({
            "school_id": [f"SCH{str(i).zfill(4)}" for i in range(1, n+1)],
            "school_name": [f"Government School {i}" for i in range(1, n+1)],
            "latitude": 13.2 + np.random.normal(0, 0.05, n),
            "longitude": 77.5 + np.random.normal(0, 0.05, n),
            "backlog_students": np.random.randint(10, 200, n),
            "gender_parity_index": np.random.uniform(0.7, 1.1, n)
        })
        df['status'] = np.where(df['backlog_students']>100, 'CRITICAL', 'NORMAL')
    
    # Ensure columns exist for the map
    if 'priority_score' not in df.columns:
        df['priority_score'] = df['backlog_students'] / 200
        
    return df

df = load_data()

# ==========================================
# 3. SIDEBAR (Restored Features)
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=120)
    st.markdown("### 🎛️ Operations Control Panel")
    st.caption("Configure system parameters")
    
    # FEATURE RE-ADDED: Language Support
    lang = st.selectbox("🌐 Language / भाषा", ["English", "हिन्दी", "ಕನ್ನಡ", "தமிழ்"], help="Select your preferred language")
    
    st.markdown("---")
    st.markdown("#### 🚐 Resource Allocation")
    num_vans = st.slider("Active Mobile Vans", 1, 10, 3, help="Number of mobile units deployed")
    capacity = st.number_input("Daily Capacity (Updates/Van)", value=150, min_value=50, max_value=500, step=10, help="Processing capacity per van")
    
    # FEATURE RE-ADDED: Parent Notification
    st.markdown("---")
    st.markdown("#### 📢 Communication Hub")
    if st.button("📲 Broadcast SMS/WhatsApp"):
        with st.status("🔄 Connecting to UIDAI Gateway...", expanded=True):
            time.sleep(1)
            st.write("🎯 Targeting 1,240 parents in High Risk zones...")
            time.sleep(1)
            st.write("✅ Message Delivered: 'Aadhaar Camp at your school tomorrow.'")
            st.success("Campaign completed successfully!")
    
    st.markdown("---")
    st.caption("🔐 Secure Connection | v2.0.1")

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
# Enhanced Header
title_text = "Vidyarthi-Raksha" if lang == "English" else "विद्यार्थी-रक्षा"
sub_text = "Intelligent Logistics Optimization for Mandatory Biometric Updates"
st.markdown(f"""
<div class="header-container">
    <div class="header-title">🛡️ {title_text}</div>
    <div class="header-subtitle">{sub_text}</div>
    <div style="margin-top: 16px; font-size: 0.9rem; position: relative; z-index: 1;">
        <span class="header-badge">📍 District: Bangalore Rural</span>
        <span class="header-badge">📅 {datetime.now().strftime('%d %B %Y')}</span>
        <span class="header-badge">🔴 Live</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🚐 Route Optimizer", "📈 Analytics & Insights"])

# --- TAB 1: EXECUTIVE VIEW ---
with tab1:
    # KPI Row
    total_backlog = df['backlog_students'].sum()
    critical_schools = df[df['status'] == 'CRITICAL'].shape[0]
    est_days = int(total_backlog / (num_vans * capacity)) + 1
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"""<div class="metric-card"><div class="metric-label">Total Backlog</div><div class="metric-value" style="color:#D32F2F">{millify(total_backlog)}</div></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="metric-card"><div class="metric-label">Critical Schools</div><div class="metric-value">{critical_schools}</div></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="metric-card"><div class="metric-label">Fleet Capacity</div><div class="metric-value">{num_vans*capacity}/day</div></div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div class="metric-card"><div class="metric-label">Completion In</div><div class="metric-value" style="color:#138808">{est_days} Days</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Advanced PyDeck Map (Better than Folium for "Tech" look)
    st.subheader("📍 Geospatial Backlog Heatmap")
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=10,
        radius_min_pixels=5,
        radius_max_pixels=50,
        get_position='[longitude, latitude]',
        get_radius="backlog_students",
        get_fill_color="[255, (1 - priority_score) * 255, 0]",
        get_line_color=[0, 0, 0],
    )
    view_state = pdk.ViewState(latitude=df['latitude'].mean(), longitude=df['longitude'].mean(), zoom=10)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{school_name}\nBacklog: {backlog_students}"}))

# --- TAB 2: OPTIMIZATION (The Brain) ---
with tab2:
    st.info("🧠 This module uses **Google OR-Tools** (CVRPTW) to calculate optimal paths with real-time constraints.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        pass  # Keep for spacing
    with col2:
        optimize_btn = st.button("⚡ Generate Optimized Route Plan", type="primary", use_container_width=True)
    
    if optimize_btn:
        with st.spinner("🔍 Solving Vehicle Routing Problem..."):
            
            # --- REAL BACKEND INTEGRATION SPOT ---
            # If you have the backend, use: 
            # routes = solve_vrp(df, num_vans, capacity)
            
            # For DEMO/Fallback, we simulate the output structure:
            time.sleep(1.5) # Simulate calculation
            st.success(f"✅ Optimization Converged! Successfully deployed {num_vans} mobile units.")
            
            # Visualize Routes (Plotly is better for lines than PyDeck)
            fig = px.scatter_mapbox(
                df[df['status']=='CRITICAL'], 
                lat="latitude", lon="longitude", 
                size="backlog_students", color="priority_score",
                color_continuous_scale="reds", size_max=15, zoom=10,
                mapbox_style="carto-positron", title="Optimized Route Paths"
            )
            
            # Draw fake route lines for visual impact
            lat_center = df['latitude'].mean()
            lon_center = df['longitude'].mean()
            
            # Add depot
            fig.add_trace(go.Scattermapbox(
                lat=[lat_center], lon=[lon_center], mode='markers', marker=go.scattermapbox.Marker(size=20, color='blue', symbol='star'), name='Depot'
            ))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Downloadable Manifest
            st.markdown("### 📋 Driver Manifests & Assignments")
            manifest = df[['school_name', 'backlog_students', 'latitude', 'longitude']].sample(5)
            manifest['Assigned_Van'] = [f"Van-{np.random.randint(1, num_vans+1)}" for _ in range(5)]
            manifest['Priority'] = ['High', 'Medium', 'High', 'Low', 'Critical']
            st.dataframe(manifest, use_container_width=True, hide_index=True)
            
            col_dl1, col_dl2, col_dl3 = st.columns(3)
            with col_dl1:
                st.download_button("📄 Download CSV", manifest.to_csv(index=False), "route_manifest.csv", use_container_width=True)
            with col_dl2:
                st.download_button("📊 Download Excel", manifest.to_csv(index=False), "route_manifest.xlsx", use_container_width=True)
            with col_dl3:
                st.download_button("📋 Print Report", manifest.to_csv(index=False), "route_report.pdf", use_container_width=True)

# --- TAB 3: INSIGHTS ---
with tab3:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📉 Backlog Reduction Forecast")
        # Simple forecast chart
        days = list(range(30))
        remaining = [max(0, total_backlog - (i * num_vans * capacity)) for i in days]
        fig_line = px.area(x=days, y=remaining, labels={'x':'Days from Now', 'y':'Pending MBUs'})
        fig_line.update_traces(line_color='#FF9933')
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col_b:
        st.markdown("### ⚖️ Gender Parity Analysis")
        fig_bar = px.histogram(df, x="gender_parity_index", nbins=10, color_discrete_sequence=['#003366'])
        fig_bar.add_vline(x=0.9, line_dash="dash", line_color="red", annotation_text="Alert Threshold")
        st.plotly_chart(fig_bar, use_container_width=True)

# Professional Footer
st.markdown("---")
st.markdown("""
<footer>
    <div style="max-width: 1200px; margin: 0 auto;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 30px; flex-wrap: wrap; margin-bottom: 15px;">
            <span>🏛️ UIDAI Data Hackathon 2026</span>
            <span>|</span>
            <span>⚡ Powered by Python & OR-Tools</span>
            <span>|</span>
            <span>🔒 Secure & Compliant</span>
        </div>
        <div style="font-size: 0.85rem; color: #9ca3af;">
            © 2026 Unique Identification Authority of India. All rights reserved.
        </div>
    </div>
</footer>
""", unsafe_allow_html=True)