import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- PAGE CONFIGURATION (Must be first) ---
st.set_page_config(
    page_title="Vidyarthi-Raksha | UIDAI Command Center",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=150)
    st.title("Operations Control")
    
    selected_district = st.selectbox("Select District",)
    
    st.divider()
    
    st.header("Resource Deployment")
    num_vans = st.slider("Available Biometric Vans", 1, 10, 3)
    daily_capacity = st.number_input("Updates per Van/Day", value=50)
    
    if st.button("🚀 Optimize Deployment Routes", type="primary"):
        st.session_state['optimized'] = True
        st.success(f"Deployed {num_vans} vans for optimization.")

# --- MAIN DASHBOARD ---

# 1. Header Section
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("## 🛡️ Vidyarthi-Raksha : Student Biometric Compliance System")
    st.markdown(f"**District View:** {selected_district} | **Status:** Live Monitoring")
with col2:
    # Top right metric style
    st.markdown("### 🔴 High Risk Zones: 14")

st.divider()

# Load Data
try:
    df = pd.read_csv("mock_school_data.csv")
except FileNotFoundError:
    st.error("Please run generate_mock_data.py first!")
    st.stop()

# 2. Key Metrics Row (The "Bureaucrat View")
total_pending = df['pending_mbu'].sum()
high_risk_schools = df[df['risk_level'] == 'High'].shape
est_days = int(total_pending / (num_vans * daily_capacity))

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Pending MBUs", f"{total_pending}", "+124 today")
m2.metric("Critical Schools", f"{high_risk_schools}", "Needs Immediate Action", delta_color="inverse")
m3.metric("Fleet Efficiency", "92%", "High")
m4.metric("Est. Time to Clear", f"{est_days} Days", f"with {num_vans} vans")

# 3. The Map Interaction (The "Wow" Factor)
st.subheader("📍 Live Geospatial Deployment Plan")

# Map Logic
m = folium.Map(location=[13.2, 77.5], zoom_start=10, tiles="cartodbpositron")

# Add markers for schools
for index, row in df.iterrows():
    color = "red" if row['risk_level'] == "High" else "green"
    radius = 8 if row['risk_level'] == "High" else 4
    
    # Tooltip content
    tooltip_html = f"""
    <b>{row['school_name']}</b><br>
    Pending MBUs: {row['pending_mbu']}<br>
    Status: {row['risk_level']}
    """
    
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        tooltip=tooltip_html
    ).add_to(m)

# SIMULATE ROUTES (If button clicked)
if st.session_state.get('optimized'):
    # Filter high risk schools to draw lines between them (Mocking the route)
    high_risk_df = df[df['risk_level'] == 'High'].head(5) # Take top 5 for demo
    route_points = high_risk_df[['lat', 'lon']].values.tolist()
    
    # Draw the path
    folium.PolyLine(
        route_points,
        color="blue",
        weight=4,
        opacity=0.8,
        tooltip="Van Route A - Schedule: Tomorrow"
    ).add_to(m)
    
    # Add a "Van" icon at the start
    folium.Marker(
        location=route_points,
        icon=folium.Icon(color="blue", icon="truck", prefix="fa"),
        tooltip="Mobile Unit 1"
    ).add_to(m)

# Render Map
st_data = st_folium(m, width="100%", height=500)

# 4. Actionable Table
with st.expander("📋 View Detailed Deployment Schedule", expanded=True):
    st.dataframe(
        df[df['risk_level'] == 'High'][['school_name', 'pending_mbu', 'total_students']],
        column_config={
            "pending_mbu": st.column_config.ProgressColumn("Backlog Severity", format="%d", min_value=0, max_value=200),
        },
        use_container_width=True
    )