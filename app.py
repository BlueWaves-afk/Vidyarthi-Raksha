"""
Vidyarthi-Raksha: UIDAI Command Center
========================================
Intelligent Logistics Optimization for Mandatory Biometric Updates

Phase 4: Interface & Visualization Integration
- Tab 1: Strategic Command Center (KPIs, geographic analysis)
- Tab 2: Tactical Operations (Route visualization, Gantt scheduling)  
- Tab 3: Analytical Intelligence (Forecasting, equity metrics)
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import math
from pathlib import Path
from datetime import datetime
import streamlit_antd_components as sac

# Import core modules
from core.data_engine import generate_digital_twin_dataset
from core.optimization import RouteOptimizer

# Import view modules
from views.tab1_command import render_tab1
from views.tab2_operations import render_tab2
from views.tab3_intelligence import render_tab3

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Vidyarthi-Raksha | UIDAI Command Center",
    page_icon="https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. STYLING & THEME (LIGHT MODE)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #f5f7fa;
        --card-bg: #ffffff;
        --sidebar-bg: #f1f5f9;
        --sidebar-component-bg: #e8ecf1;
        --sidebar-border: #dce3eb;
        --sidebar-text: #344767;
        --sidebar-text-muted: #7b809a;
        --text-dark: #344767;
        --text-muted: #7b809a;
        --divider: #dce3eb;
        --accent: #f59e0b;
        --accent-dark: #d97706;
        --sidebar-hover: #e2e7ed;
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    body, .main, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main {
        background: var(--bg);
        color: var(--text-dark);
        padding: 0;
    }

    .block-container {
        padding: 1.25rem 2.2rem 2.5rem;
        max-width: 100%;
        background: var(--bg);
    }

    /* ==========================================
       SIDEBAR - Consistent Grey Theme
       ========================================== */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--sidebar-border);
        min-width: 320px;
        width: 320px;
        padding: 0 !important;
        margin: 0 !important;
        flex-shrink: 0 !important;
        opacity: 1 !important;
        visibility: visible !important;
        transform: translateX(0) !important;
    }

    /* Disable Streamlit's collapse toggle for fixed government sidebar */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarNav"] button[aria-label="Hide sidebar"],
    [data-testid="stSidebarNav"] button[aria-label="Show sidebar"] {
        display: none !important;
    }

    /* Remove collapsed placeholder entirely */
    [data-testid="stSidebarCollapsed"] {
        display: none !important;
    }

    [data-testid="stSidebarContent"] {
        padding: 1rem 0.75rem !important;
        background: var(--sidebar-bg) !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--sidebar-text) !important;
    }

    /* Dividers */
    [data-testid="stSidebar"] hr {
        margin: 0.75rem 0 !important;
        border: none !important;
        border-top: 1px solid var(--divider) !important;
    }

    /* Sidebar header */
    .sidebar-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 0.5rem 0 0.75rem;
    }

    .aadhaar-logo {
        width: 80px;
        height: 80px;
        margin: 0 auto 0.5rem auto;
        display: block;
        object-fit: contain;
    }

    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--sidebar-text) !important;
        margin: 0;
    }

    .sidebar-subtitle {
        font-size: 0.75rem;
        color: var(--sidebar-text-muted) !important;
        letter-spacing: 0.04em;
        margin: 0;
    }

    /* Section labels */
    .scenario-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--sidebar-text-muted) !important;
        margin: 0.5rem 0 0.5rem;
        padding: 0 0.25rem;
        font-weight: 600;
        text-align: center;
    }

    /* ==========================================
       SAC MENU - Grey Theme Navigation
       ========================================== */
    [data-testid="stSidebar"] .ant-menu {
        background: transparent !important;
        border: none !important;
    }

    [data-testid="stSidebar"] .ant-menu-item {
        margin: 3px 0 !important;
        padding: 0.6rem 0.75rem !important;
        border-radius: 8px !important;
        height: auto !important;
        line-height: 1.5 !important;
        background: var(--sidebar-component-bg) !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stSidebar"] .ant-menu-item:hover {
        background: var(--sidebar-hover) !important;
    }

    /* Selected menu item - accent highlight */
    [data-testid="stSidebar"] .ant-menu-item-selected,
    [data-testid="stSidebar"] .ant-menu-item-selected:hover {
        background: var(--accent) !important;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3) !important;
    }

    [data-testid="stSidebar"] .ant-menu-item-selected *,
    [data-testid="stSidebar"] .ant-menu-item-selected span,
    [data-testid="stSidebar"] .ant-menu-item-selected .ant-menu-title-content {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .ant-menu-title-content {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    /* Tags in menu - grey theme */
    [data-testid="stSidebar"] .ant-tag {
        background: var(--sidebar-bg) !important;
        color: var(--sidebar-text-muted) !important;
        border: 1px solid var(--sidebar-border) !important;
        font-weight: 500;
        font-size: 0.7rem;
    }

    [data-testid="stSidebar"] .ant-menu-item-selected .ant-tag {
        background: rgba(255,255,255,0.2) !important;
        color: #ffffff !important;
        border-color: rgba(255,255,255,0.3) !important;
    }

    /* Hide left bar indicator */
    [data-testid="stSidebar"] .ant-menu-item::after {
        display: none !important;
    }

    /* ==========================================
       SAC CASCADER - Grey Theme Dropdown
       ========================================== */
    [data-testid="stSidebar"] .ant-cascader-picker,
    [data-testid="stSidebar"] .ant-select-selector {
        background: var(--sidebar-component-bg) !important;
        border: 1px solid var(--sidebar-border) !important;
        border-radius: 8px !important;
        padding: 0.4rem 0.6rem !important;
        font-size: 0.8rem !important;
    }

    [data-testid="stSidebar"] .ant-cascader-picker:hover,
    [data-testid="stSidebar"] .ant-cascader-picker-focused {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.15) !important;
    }

    /* ==========================================
       SAC SEGMENTED - Grey Theme Tabs
       ========================================== */
    [data-testid="stSidebar"] .ant-segmented {
        background: var(--sidebar-component-bg) !important;
        border-radius: 8px !important;
        padding: 3px !important;
    }

    [data-testid="stSidebar"] .ant-segmented-item {
        border-radius: 6px !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        color: var(--sidebar-text-muted) !important;
    }

    [data-testid="stSidebar"] .ant-segmented-item-selected {
        background: var(--accent) !important;
        box-shadow: 0 2px 6px rgba(245, 158, 11, 0.25) !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] .ant-segmented-item-selected * {
        color: #ffffff !important;
    }

    /* ==========================================
       EXPANDER - Grey Theme Accordion
       ========================================== */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: var(--sidebar-component-bg) !important;
        border: 1px solid var(--sidebar-border) !important;
        border-radius: 8px !important;
        margin-top: 0.5rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        padding: 0.65rem 0.75rem !important;
        background: var(--sidebar-component-bg) !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stVerticalBlock"] {
        padding: 0 0.5rem 0.5rem !important;
        background: var(--sidebar-component-bg) !important;
    }

    /* ==========================================
       SELECTBOX - Grey Theme
       ========================================== */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] {
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
        background: var(--sidebar-component-bg) !important;
        border: 1px solid var(--sidebar-border) !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: var(--sidebar-component-bg) !important;
        border-color: var(--sidebar-border) !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
        border-color: var(--accent) !important;
    }

    /* ==========================================
       SLIDERS - Grey Theme
       ========================================== */
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {
        background: transparent !important;
    }

    [data-testid="stSidebar"] .stSlider label {
        font-size: 0.75rem !important;
        color: var(--sidebar-text) !important;
    }

    /* ==========================================
       POLICY INFO CARD - Grey Theme
       ========================================== */
    .policy-card {
        background: var(--sidebar-component-bg);
        border: 1px solid var(--sidebar-border);
        border-radius: 8px;
        padding: 0.75rem;
        margin-top: 0.5rem;
    }

    .policy-card-active {
        background: var(--sidebar-component-bg);
        border-left: 3px solid var(--accent);
    }

    /* ==========================================
       MAIN CONTENT AREA
       ========================================== */
    .toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 0 1.25rem;
        margin-bottom: 1.25rem;
        border-bottom: 1px solid var(--divider);
    }

    .toolbar-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--text-dark);
        letter-spacing: -0.02em;
    }

    .toolbar-subtitle {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.25rem;
        font-weight: 500;
    }

    .stButton>button {
        background: var(--accent);
        color: #ffffff;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.25rem;
        font-weight: 600;
        font-size: 0.85rem;
        box-shadow: 0 2px 6px rgba(245, 158, 11, 0.25);
        transition: all 0.15s ease;
    }

    .stButton>button:hover {
        background: var(--accent-dark);
        box-shadow: 0 4px 10px rgba(245, 158, 11, 0.35);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ==========================================
       CUSTOM LOADING CURSOR - Pinwheel Style
       ========================================== */
    /* Cursor changes to spinning pinwheel when Streamlit is processing */
    .stale-content,
    .stale-content *,
    body.cursor-loading,
    body.cursor-loading * {
        cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 100 100'%3E%3Cstyle%3E@keyframes spin %7B from %7B transform: rotate(0deg); %7D to %7B transform: rotate(360deg); %7D %7D .spinner %7B animation: spin 0.8s linear infinite; transform-origin: 50px 50px; %7D%3C/style%3E%3Cg class='spinner'%3E%3Ccircle cx='50' cy='50' r='45' fill='none' stroke='%23f59e0b' stroke-width='3' opacity='0.3'/%3E%3Cpath d='M50,50 Q50,20 25,35 Q50,50 50,50' fill='%23f59e0b'/%3E%3Cpath d='M50,50 Q80,50 65,25 Q50,50 50,50' fill='%23ffffff' stroke='%23cbd5e1' stroke-width='1'/%3E%3Cpath d='M50,50 Q50,80 75,65 Q50,50 50,50' fill='%23f59e0b'/%3E%3Cpath d='M50,50 Q20,50 35,75 Q50,50 50,50' fill='%23ffffff' stroke='%23cbd5e1' stroke-width='1'/%3E%3Ccircle cx='50' cy='50' r='5' fill='%23f59e0b'/%3E%3C/g%3E%3C/svg%3E") 12 12, wait !important;
    }

    /* Also target Streamlit's running state */
    [data-stale="true"],
    [data-stale="true"] * {
        cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 100 100'%3E%3Cstyle%3E@keyframes spin %7B from %7B transform: rotate(0deg); %7D to %7B transform: rotate(360deg); %7D %7D .spinner %7B animation: spin 0.8s linear infinite; transform-origin: 50px 50px; %7D%3C/style%3E%3Cg class='spinner'%3E%3Ccircle cx='50' cy='50' r='45' fill='none' stroke='%23f59e0b' stroke-width='3' opacity='0.3'/%3E%3Cpath d='M50,50 Q50,20 25,35 Q50,50 50,50' fill='%23f59e0b'/%3E%3Cpath d='M50,50 Q80,50 65,25 Q50,50 50,50' fill='%23ffffff' stroke='%23cbd5e1' stroke-width='1'/%3E%3Cpath d='M50,50 Q50,80 75,65 Q50,50 50,50' fill='%23f59e0b'/%3E%3Cpath d='M50,50 Q20,50 35,75 Q50,50 50,50' fill='%23ffffff' stroke='%23cbd5e1' stroke-width='1'/%3E%3Ccircle cx='50' cy='50' r='5' fill='%23f59e0b'/%3E%3C/g%3E%3C/svg%3E") 12 12, wait !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2B. LOADING CURSOR SCRIPT
# ==========================================
st.markdown("""
<script>
    (function() {
        // Watch for Streamlit's running/stale state
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes') {
                    const target = mutation.target;
                    // Check for stale attribute (Streamlit adds this when rerunning)
                    if (target.hasAttribute('data-stale') && target.getAttribute('data-stale') === 'true') {
                        document.body.classList.add('cursor-loading');
                    } else {
                        document.body.classList.remove('cursor-loading');
                    }
                }
            });
        });
        
        // Observe the app container for stale state changes
        function startObserving() {
            const appContainer = document.querySelector('[data-testid="stAppViewContainer"]');
            const stApp = document.querySelector('.stApp');
            
            if (stApp) {
                observer.observe(stApp, { attributes: true, attributeFilter: ['data-stale'] });
            }
            if (appContainer) {
                observer.observe(appContainer, { attributes: true, subtree: true });
            }
            
            // Also observe body for class changes
            observer.observe(document.body, { attributes: true, childList: true, subtree: true });
        }
        
        // Start observing when DOM is ready
        if (document.readyState === 'complete') {
            startObserving();
        } else {
            window.addEventListener('load', startObserving);
        }
        
        // Retry observation setup
        setTimeout(startObserving, 500);
        setTimeout(startObserving, 1500);
    })();
</script>
""", unsafe_allow_html=True)

# ==========================================
# 3. STATE MANAGEMENT
# ==========================================
@st.cache_data
def load_digital_twin_data():
    """Load or generate digital twin dataset."""
    return generate_digital_twin_dataset(n_schools=200)

@st.cache_resource
def init_route_optimizer():
    """Initialize route optimizer."""
    return RouteOptimizer(max_capacity=150, max_time_minutes=480)

if "mission_focus_index" not in st.session_state:
    st.session_state.mission_focus_index = [0, 0]

# ==========================================
# 4. SIDEBAR: SCENARIO PLANNING
# ==========================================
with st.sidebar:
    # Aadhaar Logo
    st.markdown("""
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png" class="aadhaar-logo">
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="sidebar-header">
            <div>
                <div class="sidebar-title">Vidyarthi-Raksha</div>
                <div class="sidebar-subtitle">Command Center</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ==========================================
    # ZONE 2: NAVIGATION MENU (sac.menu)
    # ==========================================
    st.markdown("<div class='scenario-label'>Navigation</div>", unsafe_allow_html=True)

    nav_lookup = {
        "Executive View": "Strategic",
        "Tactical View": "Tactical",
        "Analytical View": "Analytical",
    }

    nav_items = [
        sac.MenuItem(
            "Executive View",
            icon="bar-chart-line",
            tag="Strategic Dashboard",
        ),
        sac.MenuItem(
            "Tactical View",
            icon="truck",
            tag="Route Optimizer",
        ),
        sac.MenuItem(
            "Analytical View",
            icon="graph-up-arrow",
            tag="Forecasting & Trends",
        ),
    ]

    nav_labels = [item.label for item in nav_items]
    default_label = st.session_state.get("nav_choice", nav_labels[0])
    default_index = nav_labels.index(default_label) if default_label in nav_labels else 0

    nav_choice = sac.menu(
        items=nav_items,
        index=default_index,
        open_all=False,
        color="#f59e0b",
        variant="left-bar",
        size="md",
        key="nav_menu",
    )

    st.session_state.nav_choice = nav_choice
    selected_tab = nav_lookup.get(nav_choice, "Strategic")
    st.session_state.selected_tab = selected_tab
    
    st.divider()
    
    # ==========================================
    # ZONE 3: ADMINISTRATIVE FILTERS
    # State > District hierarchy for all India (drill-down style)
    # ==========================================
    st.markdown("<div class='scenario-label'>Administrative Filter</div>", unsafe_allow_html=True)
    
    # State-District data dictionary
    india_states_districts = {
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Tirupati", "Kadapa", "Anantapur", "Kakinada"],
        "Arunachal Pradesh": ["Itanagar", "Naharlagun", "Pasighat", "Tawang", "Ziro", "Bomdila"],
        "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tinsukia", "Tezpur", "Bongaigaon"],
        "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Purnia", "Darbhanga", "Bihar Sharif", "Arrah", "Begusarai"],
        "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg", "Rajnandgaon", "Jagdalpur", "Raigarh"],
        "Goa": ["Panaji", "Margao", "Vasco da Gama", "Mapusa", "Ponda"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Junagadh", "Gandhinagar", "Anand"],
        "Haryana": ["Faridabad", "Gurgaon", "Panipat", "Ambala", "Yamunanagar", "Rohtak", "Hisar", "Karnal", "Sonipat"],
        "Himachal Pradesh": ["Shimla", "Mandi", "Solan", "Dharamshala", "Kullu", "Hamirpur", "Una", "Bilaspur"],
        "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh", "Giridih", "Deoghar", "Dumka", "Ramgarh"],
        "Karnataka": ["Bangalore", "Mysore", "Hubli-Dharwad", "Mangalore", "Belgaum", "Gulbarga", "Davangere", "Bellary", "Shimoga"],
        "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam", "Palakkad", "Alappuzha", "Kannur", "Kottayam"],
        "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain", "Sagar", "Dewas", "Satna", "Ratlam"],
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", "Kolhapur", "Amravati"],
        "Manipur": ["Imphal", "Thoubal", "Bishnupur", "Churachandpur", "Kakching"],
        "Meghalaya": ["Shillong", "Tura", "Jowai", "Nongstoin", "Williamnagar"],
        "Mizoram": ["Aizawl", "Lunglei", "Champhai", "Serchhip", "Kolasib"],
        "Nagaland": ["Kohima", "Dimapur", "Mokokchung", "Tuensang", "Wokha"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur", "Puri", "Balasore", "Baripada"],
        "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Pathankot", "Hoshiarpur"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Udaipur", "Ajmer", "Bhilwara", "Alwar", "Sikar"],
        "Sikkim": ["Gangtok", "Namchi", "Gyalshing", "Mangan"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Tiruppur", "Erode", "Vellore"],
        "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Mahbubnagar", "Nalgonda", "Adilabad"],
        "Tripura": ["Agartala", "Udaipur", "Dharmanagar", "Kailasahar", "Belonia"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Ghaziabad", "Agra", "Varanasi", "Meerut", "Allahabad", "Bareilly", "Aligarh"],
        "Uttarakhand": ["Dehradun", "Haridwar", "Roorkee", "Haldwani", "Rudrapur", "Kashipur", "Rishikesh", "Nainital"],
        "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Bardhaman", "Malda", "Kharagpur"],
        "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi", "Central Delhi"],
        "Jammu & Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla", "Udhampur", "Sopore"],
        "Ladakh": ["Leh", "Kargil"],
    }
    
    states_list = list(india_states_districts.keys())
    
    # Initialize state selection
    if "selected_state" not in st.session_state:
        st.session_state.selected_state = "Jharkhand"
    if "selected_district" not in st.session_state:
        st.session_state.selected_district = "Ranchi"
    
    # State selector
    selected_state = st.selectbox(
        "State",
        options=states_list,
        index=states_list.index(st.session_state.selected_state) if st.session_state.selected_state in states_list else 0,
        key="state_selector",
        label_visibility="collapsed",
    )
    st.session_state.selected_state = selected_state
    
    # District selector (updates based on state)
    districts = india_states_districts.get(selected_state, [])
    default_district_idx = districts.index(st.session_state.selected_district) if st.session_state.selected_district in districts else 0
    
    selected_district = st.selectbox(
        "District",
        options=districts,
        index=default_district_idx,
        key="district_selector",
        label_visibility="collapsed",
    )
    st.session_state.selected_district = selected_district
    
    # Show current selection
    st.markdown(f"""
        <div style="
            background: #e8ecf1;
            border-radius: 6px;
            padding: 0.5rem 0.75rem;
            margin-top: 0.5rem;
            font-size: 0.75rem;
            color: #344767;
        ">
            <span style="color: #7b809a;">Selected:</span> {selected_state} / {selected_district}
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ==========================================
    # ZONE 4: OPTIMIZATION POLICY CONTROL
    # Technical differentiator - exposes cost vs equity trade-offs
    # ==========================================
    st.markdown("<div class='scenario-label'>Optimization Priority</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="policy-card">
            <div style="font-size: 0.75rem; color: #7b809a; line-height: 1.4;">
                Toggle between minimizing operational cost or maximizing student inclusion
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize policy mode in session state
    if 'policy_mode' not in st.session_state:
        st.session_state.policy_mode = "balanced"
    
    # Enterprise-grade segmented control using SAC
    policy_mode_selection = sac.segmented(
        items=[
            sac.SegmentedItem(label="Efficiency", icon="lightning-charge"),
            sac.SegmentedItem(label="Balanced", icon="sliders"),
            sac.SegmentedItem(label="Equity", icon="heart"),
        ],
        index={"efficiency": 0, "balanced": 1, "equity": 2}.get(st.session_state.policy_mode, 1),
        color="#f59e0b",
        size="sm",
        radius="lg",
        use_container_width=True,
        key="policy_mode_selector",
        return_index=True,
    )
    
    # Map index to mode string
    policy_index_map = {0: "efficiency", 1: "balanced", 2: "equity"}
    if policy_mode_selection is not None:
        new_mode = policy_index_map.get(policy_mode_selection, "balanced")
        if new_mode != st.session_state.policy_mode:
            st.session_state.policy_mode = new_mode
            st.rerun()
    
    current_mode = st.session_state.policy_mode
    
    # Policy mode info cards
    mode_info = {
        "efficiency": {
            "title": "Efficiency Mode",
            "subtitle": "Minimize Cost",
            "desc": "Optimizes for shortest routes and lowest fuel consumption. Urban-centric coverage.",
            "color": "#3b82f6",
            "cost_impact": "LOW",
            "equity_impact": "MODERATE",
            "cost_color": "#22c55e",
            "equity_color": "#f59e0b",
        },
        "balanced": {
            "title": "Balanced Mode", 
            "subtitle": "Cost-Equity Balance",
            "desc": "Balances operational costs with inclusion goals. Recommended for standard operations.",
            "color": "#f59e0b",
            "cost_impact": "MODERATE",
            "equity_impact": "GOOD",
            "cost_color": "#f59e0b",
            "equity_color": "#22c55e",
        },
        "equity": {
            "title": "Vidyarthi-Raksha Mode",
            "subtitle": "Maximize Inclusion",
            "desc": "Prioritizes high-risk female students in Dark Zones. Extended rural routes.",
            "color": "#dc2626",
            "cost_impact": "HIGHER",
            "equity_impact": "MAXIMUM",
            "cost_color": "#f59e0b",
            "equity_color": "#22c55e",
        },
    }
    
    info = mode_info.get(current_mode, mode_info["balanced"])
    
    st.markdown(f"""
        <div class="policy-card policy-card-active">
            <div style="margin-bottom: 0.5rem;">
                <div style="font-size: 0.85rem; font-weight: 600; color: #344767;">{info['title']}</div>
                <div style="font-size: 0.7rem; color: {info['color']}; font-weight: 500;">{info['subtitle']}</div>
            </div>
            <div style="font-size: 0.75rem; color: #7b809a; line-height: 1.4; margin-bottom: 0.75rem;">
                {info['desc']}
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <div style="
                    flex: 1;
                    background: #dce3eb;
                    border-radius: 6px;
                    padding: 0.4rem;
                    text-align: center;
                ">
                    <div style="font-size: 0.6rem; color: #7b809a; text-transform: uppercase; letter-spacing: 0.04em;">Fuel Cost</div>
                    <div style="font-size: 0.7rem; font-weight: 600; color: {info['cost_color']};">{info['cost_impact']}</div>
                </div>
                <div style="
                    flex: 1;
                    background: #dce3eb;
                    border-radius: 6px;
                    padding: 0.4rem;
                    text-align: center;
                ">
                    <div style="font-size: 0.6rem; color: #7b809a; text-transform: uppercase; letter-spacing: 0.04em;">Equity</div>
                    <div style="font-size: 0.7rem; font-weight: 600; color: {info['equity_color']};">{info['equity_impact']}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Scenario Planning Expander
    with st.expander("Scenario Planning", expanded=True):
        st.markdown("<div class='scenario-label'>Mission Focus</div>", unsafe_allow_html=True)

        # Mission focus data
        mission_categories = {
            "Mission Intensity": ["Backlog Surge", "Access Equity Sweep"],
            "Calendar Sensitivity": ["Board Exam Critical", "Seasonal Disruption"],
        }
        
        categories_list = list(mission_categories.keys())
        
        # Initialize mission focus state
        if "mission_category" not in st.session_state:
            st.session_state.mission_category = "Mission Intensity"
        if "mission_focus" not in st.session_state:
            st.session_state.mission_focus = "Backlog Surge"
        
        # Category selector
        selected_category = st.selectbox(
            "Category",
            options=categories_list,
            index=categories_list.index(st.session_state.mission_category) if st.session_state.mission_category in categories_list else 0,
            key="mission_category_selector",
            label_visibility="collapsed",
        )
        st.session_state.mission_category = selected_category
        
        # Focus selector (updates based on category)
        focus_options = mission_categories.get(selected_category, [])
        default_focus_idx = focus_options.index(st.session_state.mission_focus) if st.session_state.mission_focus in focus_options else 0
        
        selected_focus = st.selectbox(
            "Focus",
            options=focus_options,
            index=default_focus_idx,
            key="mission_focus_selector",
            label_visibility="collapsed",
        )
        st.session_state.mission_focus = selected_focus
        
        # For backward compatibility
        mission_focus_path = [selected_category, selected_focus]

        policy_pressure = st.slider(
            "Policy Urgency Index",
            min_value=0,
            max_value=100,
            value=st.session_state.get("policy_pressure", 60),
            step=5,
            help="Higher values accelerate deployments in response to policy guidance.",
        )
        st.session_state.policy_pressure = policy_pressure

        st.markdown("<div class='scenario-label'>Fleet Configuration</div>", unsafe_allow_html=True)
        
        num_vans = st.slider(
            "Number of Mobile Units",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
            help="Number of vehicles to deploy for enrollment"
        )
        
        capacity = st.slider(
            "Daily Capacity (Students/Unit)",
            min_value=50,
            max_value=500,
            value=150,
            step=10,
            help="Maximum students a vehicle can process per day"
        )
        
        st.markdown("<div class='scenario-label' style='margin-top: 1rem;'>Priority Weighting</div>", unsafe_allow_html=True)
        
        col_weight1, col_weight2 = st.columns(2)
        with col_weight1:
            backlog_weight = st.slider(
                "Backlog Weight",
                min_value=0.0,
                max_value=100.0,
                value=70.0,
                step=5.0,
                help="Emphasis on student backlog (0-100)"
            )
        
        with col_weight2:
            access_weight = st.slider(
                "Access Risk Weight",
                min_value=0.0,
                max_value=100.0,
                value=30.0,
                step=5.0,
                help="Emphasis on geographic access (0-100)"
            )
        
        # Normalize weights
        total_weight = backlog_weight + access_weight
        backlog_weight_norm = backlog_weight / total_weight if total_weight > 0 else 0.5
        access_weight_norm = access_weight / total_weight if total_weight > 0 else 0.5
        
        st.markdown("<div class='scenario-card'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size: 0.9rem; color: rgba(226, 232, 240, 0.9); margin: 0.5rem 0;">
            <strong>Daily Capacity:</strong> {num_vans * capacity:,} students/day
        </div>
        <div style="font-size: 0.9rem; color: rgba(226, 232, 240, 0.9);">
            <strong>Priority Mix:</strong> {backlog_weight_norm*100:.0f}% Backlog + {access_weight_norm*100:.0f}% Access
        </div>
        <div style="font-size: 0.9rem; color: rgba(226, 232, 240, 0.9); margin-top: 0.4rem;">
            <strong>Mission Focus:</strong> {' > '.join(mission_focus_path)}
        </div>
        <div style="font-size: 0.9rem; color: rgba(226, 232, 240, 0.9);">
            <strong>Policy Pressure:</strong> {policy_pressure}/100
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Optimize routes button
        if st.button("Optimize Routes", use_container_width=True, key="optimize_btn"):
            st.session_state.run_optimization = True
    
    st.divider()
    
    # Status panel - smaller, grey text
    st.markdown("""
        <div style="
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0.25rem;
        ">
            <div>
                <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.04em;">Version</div>
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 500;">1.0.0</div>
            </div>
            <div>
                <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.04em;">Status</div>
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 500;">Active</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. LOAD DATA
# ==========================================
selected_tab = st.session_state.get("selected_tab", "Strategic")

df = load_digital_twin_data()
optimizer = init_route_optimizer()

# Initialize routes
if 'routes_df' not in st.session_state:
    st.session_state.routes_df = pd.DataFrame()

# Run optimization if button clicked
if st.session_state.get('run_optimization', False):
    with st.spinner(f"Optimizing routes for {num_vans} vehicles..."):
        time.sleep(0.5)
        routes_list = optimizer.optimize_routes(df, num_vehicles=num_vans)
        
        # Convert routes to dataframe for display
        routes_records = []
        for route in routes_list:
            for school in route['schools']:
                routes_records.append({
                    'vehicle_id': route['vehicle_id'],
                    'school_id': school['school_id'],
                    'school_name': school['school_name'],
                    'backlog_students': school['backlog_students'],
                    'latitude': school['latitude'],
                    'longitude': school['longitude'],
                    'visit_time_minutes': school['visit_time_minutes']
                })
        
        st.session_state.routes_df = pd.DataFrame(routes_records)
        st.session_state.routes_list = routes_list
        st.session_state.run_optimization = False
        st.success(f"✅ Successfully optimized {len(routes_list)} routes!")

# ==========================================
# 6. MAIN TOOLBAR
# ==========================================
st.markdown(f"""
    <div class="toolbar">
        <div>
            <div class="toolbar-title">Vidyarthi-Raksha Dashboard</div>
            <div class="toolbar-subtitle">Aadhaar Enrollment Command Center</div>
        </div>
        <div style="text-align: right; font-size: 0.9rem; font-weight: 600; color: #1e293b;">
            {datetime.now().strftime('%d %B %Y')}
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 7. MAIN TABS
# ==========================================
# Get policy mode for all tabs
policy_mode = st.session_state.get('policy_mode', 'balanced')

if selected_tab == "Strategic":
    render_tab1(df, num_vans, capacity, policy_mode)
    
elif selected_tab == "Tactical":
    render_tab2(df, num_vans, policy_mode)
    
elif selected_tab == "Analytical":
    render_tab3(df)

# ==========================================
# 8. FOOTER
# ==========================================
st.divider()
st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0; font-size: 0.8rem; color: var(--text-muted);">
        <strong>Vidyarthi-Raksha</strong> | Intelligent Logistics Optimization for Mandatory Biometric Updates<br>
        Ministry of Rural Development | Government of India<br>
        <span style="font-size: 0.75rem; margin-top: 0.5rem;">
            Powered by Streamlit, OR-Tools, and Distributed Data Intelligence
        </span>
    </div>
""", unsafe_allow_html=True)
