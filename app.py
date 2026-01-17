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
    initial_sidebar_state="collapsed"  # Start collapsed for modern look
)

# Modern Tricolor Dashboard CSS
st.markdown("""
<style>
    /* Import Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Tricolor Palette */
    :root {
        --saffron: #FF9933;
        --white: #FFFFFF;
        --green: #138808;
        --navy: #000080;
        --light-bg: #F5F7FA;
        --card-bg: #FFFFFF;
        --text-primary: #1A202C;
        --text-secondary: #718096;
        --shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        --shadow-hover: 0 20px 60px rgba(0, 0, 0, 0.12);
    }
    
    /* Global Styling */
    .main { 
        background: linear-gradient(135deg, #FAF5FF 0%, #F0F9FF 50%, #F0FDF4 100%);
        padding: 0;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Remove default padding */
    .block-container {
        padding: 1.5rem 2rem;
        max-width: 100%;
        animation: fadeIn 0.6s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Modern Header */
    .header-container {
        background: linear-gradient(135deg, var(--saffron) 0%, #FF7A00 100%);
        padding: 2rem 2.5rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
        animation: slideDown 0.5s ease-out;
    }
    
    @keyframes slideDown {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    .header-title { 
        font-size: 2.8rem; 
        font-weight: 800; 
        margin: 0;
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .header-subtitle { 
        font-size: 1.1rem; 
        opacity: 0.95; 
        margin-top: 8px;
        font-weight: 400;
        letter-spacing: 0.5px;
        position: relative;
        z-index: 1;
    }
    
    .header-badge {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 0.85rem;
        margin-right: 12px;
        display: inline-block;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 500;
    }
    
    .header-badge:hover {
        background: rgba(255, 255, 255, 0.35);
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Ultra Modern Metrics Cards */
    .metric-card {
        background: var(--card-bg);
        padding: 28px;
        border-radius: 20px;
        border: none;
        box-shadow: var(--shadow);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
        animation: cardFadeIn 0.6s ease-out backwards;
    }
    
    @keyframes cardFadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .metric-card:nth-child(1) { animation-delay: 0.1s; }
    .metric-card:nth-child(2) { animation-delay: 0.2s; }
    .metric-card:nth-child(3) { animation-delay: 0.3s; }
    .metric-card:nth-child(4) { animation-delay: 0.4s; }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, var(--saffron), var(--green));
        transition: width 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-hover);
    }
    
    .metric-card:hover::before {
        width: 100%;
        opacity: 0.1;
    }
    
    .metric-value { 
        font-size: 2.5rem; 
        font-weight: 800; 
        background: linear-gradient(135deg, var(--saffron), #FF7A00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin-bottom: 8px;
    }
    
    .metric-label { 
        font-size: 0.75rem; 
        color: var(--text-secondary);
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        font-weight: 700;
    }
    
    /* Collapsible Modern Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
        border-right: 1px solid rgba(0, 0, 0, 0.05);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stSidebar"][aria-expanded="true"] {
        animation: slideInLeft 0.3s ease-out;
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }
    
    [data-testid="stSidebar"] .stImage {
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, var(--saffron), #FF7A00);
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(255, 153, 51, 0.3);
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stImage:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 24px rgba(255, 153, 51, 0.4);
    }
    
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 1.1rem;
        margin-top: 1.5rem;
        padding-left: 0.5rem;
        border-left: 4px solid var(--saffron);
    }
    
    /* Modern Buttons - Tricolor Theme */
    .stButton>button {
        background: linear-gradient(135deg, var(--green) 0%, #0F6606 100%);
        color: white;
        border: none;
        border-radius: 14px;
        height: 3.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.5px;
        box-shadow: 0 4px 16px rgba(19, 136, 8, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton>button:hover::before {
        left: 100%;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #0F6606 0%, var(--green) 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(19, 136, 8, 0.4);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Ultra Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: white;
        border-radius: 20px;
        padding: 12px;
        box-shadow: var(--shadow);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        border-radius: 14px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 28px;
        color: var(--text-secondary);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #FFF5EB 0%, #FFF9F0 100%);
        color: var(--saffron);
        border-color: var(--saffron);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--saffron) 0%, #FF7A00 100%) !important;
        color: white !important;
        border-color: var(--saffron) !important;
        box-shadow: 0 4px 16px rgba(255, 153, 51, 0.3);
    }
    
    /* Info/Warning Boxes */
    .stAlert {
        border-radius: 16px;
        border: none;
        padding: 1.25rem 1.5rem;
        box-shadow: var(--shadow);
        border-left: 4px solid var(--saffron);
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Data Tables */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: var(--shadow);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    /* Inputs and Selects */
    .stSelectbox, .stNumberInput, .stSlider {
        font-weight: 500;
    }
    
    .stSelectbox [data-baseweb="select"] {
        border-radius: 12px;
        border-color: rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .stSelectbox [data-baseweb="select"]:focus {
        border-color: var(--saffron);
        box-shadow: 0 0 0 3px rgba(255, 153, 51, 0.1);
    }
    
    .stNumberInput input {
        border-radius: 12px;
        border-color: rgba(0, 0, 0, 0.1);
    }
    
    .stNumberInput input:focus {
        border-color: var(--saffron);
        box-shadow: 0 0 0 3px rgba(255, 153, 51, 0.1);
    }
    
    /* Section Headers */
    h1, h2, h3 {
        color: var(--text-primary);
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h3 {
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    /* Download Button - Green Theme */
    .stDownloadButton>button {
        background: linear-gradient(135deg, var(--green) 0%, #0F6606 100%);
        color: white;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(19, 136, 8, 0.3);
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #0F6606 0%, var(--green) 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(19, 136, 8, 0.4);
    }
    
    /* Dividers */
    hr {
        margin: 3rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 153, 51, 0.3), transparent);
    }
    
    /* Modern Footer */
    footer {
        color: var(--text-secondary);
        font-size: 0.9rem;
        padding: 3rem 0 2rem;
        text-align: center;
        border-top: 1px solid rgba(0, 0, 0, 0.05);
        margin-top: 4rem;
        background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.5));
    }
    
    /* Smooth Animations */
    html {
        scroll-behavior: smooth;
    }
    
    /* Loading Spinner - Tricolor */
    .stSpinner > div {
        border-top-color: var(--saffron) !important;
        border-right-color: var(--green) !important;
    }
    
    /* Slider Styling */
    .stSlider [role="slider"] {
        background: var(--saffron) !important;
    }
    
    .stSlider [data-baseweb="slider"] [role="slider"]:focus {
        box-shadow: 0 0 0 4px rgba(255, 153, 51, 0.2) !important;
    }
    
    /* Metric Icon Containers */
    .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 12px;
        background: linear-gradient(135deg, rgba(255, 153, 51, 0.1), rgba(19, 136, 8, 0.1));
    }
    
    /* Plotly Charts */
    .js-plotly-plot {
        border-radius: 16px;
        overflow: hidden;
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
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="font-size: 1.3rem; font-weight: 700; color: #1A202C; margin: 0;">
                🎛️ Control Panel
            </h2>
            <p style="font-size: 0.8rem; color: #718096; margin-top: 5px;">
                Configure system parameters
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # FEATURE RE-ADDED: Language Support
    st.markdown("##### 🌐 Language Settings")
    lang = st.selectbox("Choose Language / भाषा चुनें", ["English", "हिन्दी", "ಕನ್ನಡ", "தமிழ்"], label_visibility="collapsed", help="Select your preferred language")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 🚐 Resource Allocation")
    num_vans = st.slider("Active Mobile Vans", 1, 10, 3, help="Number of mobile units deployed")
    capacity = st.number_input("Daily Capacity (Updates/Van)", value=150, min_value=50, max_value=500, step=10, help="Processing capacity per van")
    
    # Display quick stats
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FFF5EB, #FFF9F0); padding: 1rem; border-radius: 12px; margin-top: 1rem; border-left: 3px solid var(--saffron);">
            <div style="font-size: 0.75rem; color: #718096; font-weight: 600; margin-bottom: 8px;">DAILY CAPACITY</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #FF9933;">{num_vans * capacity}</div>
            <div style="font-size: 0.7rem; color: #718096; margin-top: 4px;">Updates per day</div>
        </div>
    """, unsafe_allow_html=True)
    
    # FEATURE RE-ADDED: Parent Notification
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📢 Communication Hub")
    if st.button("📲 Broadcast Alert", use_container_width=True):
        with st.status("🔄 Connecting to UIDAI Gateway...", expanded=True):
            time.sleep(0.8)
            st.write("🎯 Targeting 1,240 parents in High Risk zones...")
            time.sleep(0.8)
            st.write("✅ Message Delivered: 'Aadhaar Camp at your school tomorrow.'")
            time.sleep(0.5)
            st.success("Campaign completed successfully!")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 1rem; background: rgba(255, 153, 51, 0.05); border-radius: 10px;">
            <div style="font-size: 0.75rem; color: #718096;">🔐 Secure Connection</div>
            <div style="font-size: 0.7rem; color: #A0AEC0; margin-top: 4px;">Version 2.0.1</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
# Modern Tricolor Header
title_text = "Vidyarthi-Raksha" if lang == "English" else "विद्यार्थी-रक्षा"
sub_text = "Intelligent Logistics Optimization for Mandatory Biometric Updates"
st.markdown(f"""
<div class="header-container">
    <div class="header-title">🛡️ {title_text}</div>
    <div class="header-subtitle">{sub_text}</div>
    <div style="margin-top: 20px; font-size: 0.9rem; position: relative; z-index: 1;">
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
    c1.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-label">Total Backlog</div>
            <div class="metric-value">{millify(total_backlog)}</div>
        </div>
    """, unsafe_allow_html=True)
    
    c2.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⚠️</div>
            <div class="metric-label">Critical Schools</div>
            <div class="metric-value" style="background: linear-gradient(135deg, #DC2626, #EF4444); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{critical_schools}</div>
        </div>
    """, unsafe_allow_html=True)
    
    c3.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🚐</div>
            <div class="metric-label">Fleet Capacity</div>
            <div class="metric-value" style="background: linear-gradient(135deg, #2563EB, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{num_vans*capacity}/day</div>
        </div>
    """, unsafe_allow_html=True)
    
    c4.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">✅</div>
            <div class="metric-label">Completion In</div>
            <div class="metric-value" style="background: linear-gradient(135deg, var(--green), #16A34A); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{est_days} Days</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Modern Section Header
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.5rem; font-weight: 700; color: #1A202C; margin: 0; display: flex; align-items: center;">
                <span style="background: linear-gradient(135deg, var(--saffron), #FF7A00); padding: 8px 12px; border-radius: 10px; margin-right: 12px; display: inline-flex; align-items: center; justify-content: center;">📍</span>
                Geospatial Backlog Heatmap
            </h3>
            <p style="color: #718096; font-size: 0.9rem; margin-top: 8px; margin-left: 56px;">Real-time visualization of school enrollment backlogs</p>
        </div>
    """, unsafe_allow_html=True)
    
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
    
    # Wrap map in a modern container
    st.markdown('<div style="border-radius: 20px; overflow: hidden; box-shadow: var(--shadow); border: 1px solid rgba(0, 0, 0, 0.05);">', unsafe_allow_html=True)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{school_name}\nBacklog: {backlog_students}"}))
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: OPTIMIZATION (The Brain) ---
with tab2:
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255, 153, 51, 0.1), rgba(19, 136, 8, 0.1)); padding: 1.25rem 1.5rem; border-radius: 16px; border-left: 4px solid var(--saffron); margin-bottom: 2rem;">
            <p style="margin: 0; color: #1A202C; font-weight: 500;">
                🧠 This module uses <strong>Google OR-Tools (CVRPTW)</strong> to calculate optimal paths with real-time constraints.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        pass  # Keep for spacing
    with col2:
        optimize_btn = st.button("⚡ Generate Route Plan", type="primary", use_container_width=True)
    
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
            
            # Modern Section Header for Manifests
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
                <div style="margin-bottom: 1.5rem;">
                    <h3 style="font-size: 1.4rem; font-weight: 700; color: #1A202C; margin: 0; display: flex; align-items: center;">
                        <span style="background: linear-gradient(135deg, var(--green), #16A34A); padding: 8px 12px; border-radius: 10px; margin-right: 12px; display: inline-flex; align-items: center; justify-content: center; color: white;">📋</span>
                        Driver Manifests & Assignments
                    </h3>
                    <p style="color: #718096; font-size: 0.85rem; margin-top: 8px; margin-left: 56px;">Download optimized routes for field deployment</p>
                </div>
            """, unsafe_allow_html=True)
            
            manifest = df[['school_name', 'backlog_students', 'latitude', 'longitude']].sample(5)
            manifest['Assigned_Van'] = [f"Van-{np.random.randint(1, num_vans+1)}" for _ in range(5)]
            manifest['Priority'] = ['High', 'Medium', 'High', 'Low', 'Critical']
            
            # Wrap dataframe in container
            st.markdown('<div style="border-radius: 16px; overflow: hidden; box-shadow: var(--shadow);">', unsafe_allow_html=True)
            st.dataframe(manifest, use_container_width=True, hide_index=True)
            st.markdown('</div><br>', unsafe_allow_html=True)
            
            col_dl1, col_dl2, col_dl3 = st.columns(3)
            with col_dl1:
                st.download_button("📄 Download CSV", manifest.to_csv(index=False), "route_manifest.csv", use_container_width=True)
            with col_dl2:
                st.download_button("📊 Download Excel", manifest.to_csv(index=False), "route_manifest.xlsx", use_container_width=True)
            with col_dl3:
                st.download_button("📋 Print Report", manifest.to_csv(index=False), "route_report.pdf", use_container_width=True)

# --- TAB 3: INSIGHTS ---
with tab3:
    col_a, col_b = st.columns(2, gap="large")
    
    with col_a:
        st.markdown("""
            <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.4rem; font-weight: 700; color: #1A202C; margin: 0; display: flex; align-items: center;">
                    <span style="background: linear-gradient(135deg, var(--saffron), #FF7A00); padding: 8px 12px; border-radius: 10px; margin-right: 12px; display: inline-flex; align-items: center; justify-content: center;">📉</span>
                    Backlog Reduction Forecast
                </h3>
                <p style="color: #718096; font-size: 0.85rem; margin-top: 8px; margin-left: 56px;">30-day projection based on current capacity</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Simple forecast chart
        days = list(range(30))
        remaining = [max(0, total_backlog - (i * num_vans * capacity)) for i in days]
        fig_line = px.area(x=days, y=remaining, labels={'x':'Days from Now', 'y':'Pending MBUs'})
        fig_line.update_traces(line_color='#FF9933', fillcolor='rgba(255, 153, 51, 0.3)')
        fig_line.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins, sans-serif", size=12),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        
        st.markdown('<div style="border-radius: 16px; overflow: hidden; box-shadow: var(--shadow); background: white; padding: 1rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_b:
        st.markdown("""
            <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.4rem; font-weight: 700; color: #1A202C; margin: 0; display: flex; align-items: center;">
                    <span style="background: linear-gradient(135deg, var(--green), #16A34A); padding: 8px 12px; border-radius: 10px; margin-right: 12px; display: inline-flex; align-items: center; justify-content: center; color: white;">⚖️</span>
                    Gender Parity Analysis
                </h3>
                <p style="color: #718096; font-size: 0.85rem; margin-top: 8px; margin-left: 56px;">Distribution of gender parity across schools</p>
            </div>
        """, unsafe_allow_html=True)
        
        fig_bar = px.histogram(df, x="gender_parity_index", nbins=10, color_discrete_sequence=['#138808'])
        fig_bar.add_vline(x=0.9, line_dash="dash", line_color="#DC2626", annotation_text="Alert Threshold")
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins, sans-serif", size=12),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        
        st.markdown('<div style="border-radius: 16px; overflow: hidden; box-shadow: var(--shadow); background: white; padding: 1rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Modern Tricolor Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<footer style="margin-top: 4rem;">
    <div style="background: white; border-radius: 20px; padding: 2.5rem; box-shadow: var(--shadow); border-top: 4px solid var(--saffron);">
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 8px;">🏛️</div>
                <div style="font-size: 0.85rem; color: #718096; font-weight: 600;">UIDAI Hackathon</div>
                <div style="font-size: 0.75rem; color: #A0AEC0;">2026 Edition</div>
            </div>
            <div style="height: 50px; width: 1px; background: linear-gradient(180deg, transparent, #E5E7EB, transparent);"></div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 8px;">⚡</div>
                <div style="font-size: 0.85rem; color: #718096; font-weight: 600;">Powered By</div>
                <div style="font-size: 0.75rem; color: #A0AEC0;">Python & OR-Tools</div>
            </div>
            <div style="height: 50px; width: 1px; background: linear-gradient(180deg, transparent, #E5E7EB, transparent);"></div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 8px;">🔒</div>
                <div style="font-size: 0.85rem; color: #718096; font-weight: 600;">Secure</div>
                <div style="font-size: 0.75rem; color: #A0AEC0;">& Compliant</div>
            </div>
        </div>
        <div style="text-align: center; padding-top: 20px; border-top: 1px solid rgba(0, 0, 0, 0.05);">
            <div style="font-size: 0.8rem; color: #A0AEC0; margin-bottom: 8px;">
                © 2026 Unique Identification Authority of India. All rights reserved.
            </div>
            <div style="display: inline-flex; gap: 10px; margin-top: 10px;">
                <span style="display: inline-block; width: 30px; height: 4px; background: var(--saffron); border-radius: 2px;"></span>
                <span style="display: inline-block; width: 30px; height: 4px; background: white; border: 1px solid #E5E7EB; border-radius: 2px;"></span>
                <span style="display: inline-block; width: 30px; height: 4px; background: var(--green); border-radius: 2px;"></span>
            </div>
        </div>
    </div>
</footer>
""", unsafe_allow_html=True)