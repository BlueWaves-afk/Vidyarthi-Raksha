import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from optimizer import solve_vrp
import time

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Vidyarthi-Raksha | UIDAI",
    page_icon="🇮🇳",
    layout="wide"
)

# -------------------------------------------------
# THEME (Govt look)
# -------------------------------------------------
st.markdown("""
<style>
.main-header {font-size: 2.5rem; color: #003366; font-weight: bold;}
.sub-header {font-size: 1.2rem; color: #F26522;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png",
        width=120
    )
    st.markdown("### Operations Control")

    lang = st.selectbox(
        "🌐 Language / भाषा",
        ["English", "हिन्दी", "ಕನ್ನಡ"]
    )

    st.divider()

    st.markdown("#### 🚑 Fleet Management")
    num_vans = st.slider("Active Mobile Vans", 1, 10, 3)
    capacity = st.number_input("Daily Capacity (Updates/Van)", 50, 500, 150)

    run_optim = st.button("⚡ Generate Optimization Plan", type="primary")
    st.info("💡 Prioritizes schools with high biometric backlog.")

# -------------------------------------------------
# DATA LOADING (cached)
# -------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("mock_school_data.csv")

try:
    df = load_data()
except Exception:
    st.error("Data not found. Run data generator first.")
    st.stop()

# -------------------------------------------------
# HEADER
# -------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="main-header">🛡️ Vidyarthi-Raksha</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI‑Driven Logistics for Mandatory Biometric Updates</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(f"**Date:** {pd.Timestamp.now().strftime('%d‑%b‑%Y')}")
    st.markdown("**District:** Bangalore Rural")

st.divider()

# -------------------------------------------------
# METRICS
# -------------------------------------------------
high_risk = df[df["risk_level"] == "High"]
total_backlog = high_risk["pending_mbu"].sum()

daily_capacity = max(num_vans * capacity, 1)
est_days = int(total_backlog / daily_capacity) + 1

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Pending MBUs", total_backlog)
m2.metric("High‑Risk Schools", len(high_risk))
m3.metric("Fleet Capacity", f"{daily_capacity}/day")
m4.metric("Est. Completion", f"{est_days} Days")

# -------------------------------------------------
# MAP
# -------------------------------------------------
st.subheader("📍 Geospatial Deployment Map")

m = folium.Map(
    location=[13.20, 77.55],
    zoom_start=11,
    tiles="cartodbpositron"
)

for _, row in df.iterrows():
    if row["risk_level"] == "High":
        color, icon = "red", "exclamation-sign"
    else:
        color, icon = "green", "ok-sign"

    folium.Marker(
        [row["lat"], row["lon"]],
        tooltip=f"{row['school_name']} ({row['pending_mbu']} pending)",
        icon=folium.Icon(color=color, icon=icon)
    ).add_to(m)

# -------------------------------------------------
# OPTIMIZATION
# -------------------------------------------------
if run_optim:
    with st.spinner("🤖 Optimizing routes using Google OR‑Tools..."):
        time.sleep(1)
        routes = solve_vrp(df, num_vans, capacity)

    if routes:
        colors = ["blue", "purple", "orange", "darkgreen"]
        for idx, route in enumerate(routes):
            if len(route) < 2:
                continue

            path = [[p["lat"], p["lon"]] for p in route]
            folium.PolyLine(
                path,
                color=colors[idx % len(colors)],
                weight=5,
                opacity=0.7,
                tooltip=f"Van {idx+1}"
            ).add_to(m)

        st.success(f"✅ Optimization complete — {len(routes)} vans deployed.")
        st.session_state["routes"] = routes
    else:
        st.warning("No high‑risk schools found for optimization.")

st_folium(m, width="100%", height=500)

# -------------------------------------------------
# ACTION CENTER
# -------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("📋 Deployment Schedule")
    if "routes" in st.session_state:
        schedule_data = []
        for i, route in enumerate(st.session_state["routes"]):
            for stop in route[1:-1]:
                schedule_data.append({
                    "Van ID": f"Van-{i+1}",
                    "School": stop["school_name"],
                    "Pending MBU": stop["pending_mbu"]
                })

        st.dataframe(pd.DataFrame(schedule_data), height=250)
    else:
        st.info("Run optimization to generate schedule.")

with c2:
    st.subheader("📢 Communication & Export")

    if st.button("📲 Send Parent Notifications"):
        with st.status("Sending messages...", expanded=True):
            time.sleep(1)
            st.write("✅ Notifications dispatched successfully.")

    st.divider()

    if "routes" in st.session_state:
        csv = pd.DataFrame(schedule_data).to_csv(index=False).encode("utf‑8")
        st.download_button(
            "📄 Download Daily Route Plan",
            csv,
            "route_plan.csv",
            "text/csv"
        )
    else:
        st.button("📄 Download Daily Route Plan", disabled=True)
