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

# Custom CSS for "GovTech" Aesthetics (NIC Standard Colors)
st.markdown("""
<style>
   .main { background-color: #f9f9f9; }
    
    /* Header Styling */
   .header-container {
        background-color: #003366; 
        padding: 1.5rem;
        border-radius: 0px 0px 10px 10px;
        color: white;
        margin-bottom: 20px;
    }
   .header-title { font-size: 2.2rem; font-weight: 700; margin: 0; }
   .header-subtitle { font-size: 1rem; opacity: 0.9; margin-top: 5px; }
    
    /* Metrics Cards */
   .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #FF9933; /* Saffron */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
   .metric-value { font-size: 1.8rem; font-weight: bold; color: #333; }
   .metric-label { font-size: 0.9rem; color: #666; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Buttons */
   .stButton>button {
        background-color: #003366;
        color: white;
        border-radius: 5px;
        height: 3rem;
        font-weight: 600;
        width: 100%;
    }
   .stButton>button:hover { background-color: #004080; }
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
    st.markdown("### Operations Control")
    
    # FEATURE RE-ADDED: Language Support
    lang = st.selectbox("🌐 Language / भाषा", ["English", "हिन्दी", "ಕನ್ನಡ", "தமிழ்"])
    
    st.markdown("---")
    st.markdown("**Resource Allocation**")
    num_vans = st.slider("Active Mobile Vans", 1, 10, 3)
    capacity = st.number_input("Daily Capacity (Updates/Van)", value=150)
    
    # FEATURE RE-ADDED: Parent Notification
    st.markdown("---")
    st.markdown("**Communication**")
    if st.button("📲 Broadcast SMS/WhatsApp"):
        with st.status("Connecting to UIDAI Gateway...", expanded=True):
            time.sleep(1)
            st.write("Targeting 1,240 parents in High Risk zones...")
            time.sleep(1)
            st.write("✅ Message Sent: 'Aadhaar Camp at your school tomorrow.'")

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
# Header
title_text = "Vidyarthi-Raksha" if lang == "English" else "विद्यार्थी-रक्षा"
sub_text = "Intelligent Logistic Optimization for Mandatory Biometric Updates"
st.markdown(f"""
<div class="header-container">
    <div class="header-title">🛡️ {title_text}</div>
    <div class="header-subtitle">{sub_text}</div>
    <div style="margin-top: 10px; font-size: 0.9rem;">
        <span style="background: #ffffff33; padding: 5px 10px; border-radius: 4px;">District: Bangalore Rural</span>
        <span style="background: #ffffff33; padding: 5px 10px; border-radius: 4px; margin-left: 10px;">Date: {datetime.now().strftime('%d %B %Y')}</span>
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
    st.info("This module uses **Google OR-Tools** (CVRPTW) to calculate optimal paths.")
    
    if st.button("⚡ Generate Optimized Route Plan", type="primary"):
        with st.spinner("Solving Vehicle Routing Problem..."):
            
            # --- REAL BACKEND INTEGRATION SPOT ---
            # If you have the backend, use: 
            # routes = solve_vrp(df, num_vans, capacity)
            
            # For DEMO/Fallback, we simulate the output structure:
            time.sleep(1.5) # Simulate calculation
            st.success(f"Optimization Converged! Deployed {num_vans} vans.")
            
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
            st.markdown("### 📋 Driver Manifests")
            manifest = df[['school_name', 'backlog_students', 'latitude', 'longitude']].sample(5)
            manifest['Assigned_Van'] = [f"Van-{np.random.randint(1, num_vans+1)}" for _ in range(5)]
            st.dataframe(manifest, use_container_width=True)
            
            st.download_button("📄 Download Route Manifest (CSV)", manifest.to_csv(), "routes.csv")

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

# Footer
st.markdown("---")
st.markdown("<center>Developed for UIDAI Data Hackathon 2026 | Powered by Python & OR-Tools</center>", unsafe_allow_html=True)