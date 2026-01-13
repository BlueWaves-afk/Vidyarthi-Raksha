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
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png",
        width=150
    )
    st.title("Operations Control")

    districts = ["Bangalore Rural", "Bangalore Urban", "Ramanagara"]
    selected_district = st.selectbox("Select District", districts)

    st.divider()
    st.header("Resource Deployment")

    num_vans = st.slider("Available Biometric Vans", 1, 10, 3)
    daily_capacity = st.number_input("Updates per Van/Day", value=50)

    if st.button("🚀 Optimize Deployment Routes", type="primary"):
        st.session_state["optimized"] = True
        st.success(f"Deployed {num_vans} vans for optimization.")

# --- MAIN DASHBOARD ---

# Header
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("## 🛡️ Vidyarthi-Raksha : Student Biometric Compliance System")
    st.markdown(f"**District View:** {selected_district} | **Status:** Live Monitoring")

with col2:
    st.markdown("### 🔴 High Risk Zones: 14")

st.divider()

# Load Data
try:
    df = pd.read_csv("mock_school_data.csv")
except FileNotFoundError:
    st.error("Please run generate_mock_data.py first!")
    st.stop()

# Metrics
total_pending = df["pending_mbu"].sum()
high_risk_schools = df[df["risk_level"] == "High"].shape[0]
est_days = int(total_pending / (num_vans * daily_capacity))

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Pending MBUs", total_pending, "+124 today")
m2.metric("Critical Schools", high_risk_schools, "Needs Immediate Action", delta_color="inverse")
m3.metric("Fleet Efficiency", "92%", "High")
m4.metric("Est. Time to Clear", f"{est_days} Days", f"with {num_vans} vans")

# Map
st.subheader("📍 Live Geospatial Deployment Plan")
m = folium.Map(location=[13.2, 77.5], zoom_start=10, tiles="cartodbpositron")

for _, row in df.iterrows():
    color = "red" if row["risk_level"] == "High" else "green"
    radius = 8 if row["risk_level"] == "High" else 4

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        tooltip=f"""
        <b>{row['school_name']}</b><br>
        Pending MBUs: {row['pending_mbu']}<br>
        Status: {row['risk_level']}
        """
    ).add_to(m)

# Simulated routes
if st.session_state.get("optimized"):
    high_risk_df = df[df["risk_level"] == "High"].head(5)
    route_points = high_risk_df[["lat", "lon"]].values.tolist()

    folium.PolyLine(
        route_points,
        color="blue",
        weight=4,
        opacity=0.8,
        tooltip="Van Route A - Schedule: Tomorrow"
    ).add_to(m)

    folium.Marker(
        location=route_points[0],
        icon=folium.Icon(color="blue", icon="truck", prefix="fa"),
        tooltip="Mobile Unit 1"
    ).add_to(m)

st_folium(m, width="100%", height=500)

# Table
with st.expander("📋 View Detailed Deployment Schedule", expanded=True):
    st.dataframe(
        df[df["risk_level"] == "High"][["school_name", "pending_mbu", "total_students"]],
        use_container_width=True
    )
