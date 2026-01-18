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
    @import url('https://fonts.googleapis.com/css2?family=Hind:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #f5f7fa;
        --card-bg: #ffffff;
        --sidebar-bg: #f1f5f9;
        --sidebar-border: #e2e8f0;
        --sidebar-text: #1a202c;
        --text-dark: #1a202c;
        --text-muted: #64748b;
        --divider: rgba(0, 0, 0, 0.08);
        --accent: #f59e0b;
        --accent-dark: #d97706;
        --sidebar-hover: rgba(0, 0, 0, 0.04);
    }

    * {
        font-family: 'Inter', 'Hind', -apple-system, BlinkMacSystemFont, sans-serif;
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

    [data-testid="stSidebar"] {
        background: var(--sidebar-bg);
        border-right: 1px solid var(--sidebar-border);
        min-width: 340px;
        width: 340px;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* FORCE remove ALL padding from every sidebar element */
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebar"] .element-container,
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"],
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] .stSlider,
    [data-testid="stSidebar"] .stRadio,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] section,
    [data-testid="stSidebar"] div {
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        box-sizing: border-box !important;
    }

    /* Exception: Allow expander some padding to prevent vibration */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] > div {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stVerticalBlock"] {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* Force sidebar content wrapper to have no padding */
    [data-testid="stSidebarContent"] {
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }

    /* Make dividers span the full sidebar width */
    [data-testid="stSidebar"] hr {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        border-color: var(--sidebar-border) !important;
    }

    /* Force divider to have no spacing */
    [data-testid="stSidebar"] hr + * {
        margin-top: 0.4rem !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--sidebar-text) !important;
    }

    .sidebar-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 0;
        margin-bottom: 0.4rem;
        padding: 0.8rem 0.5rem 0.6rem;
        border-bottom: 1px solid var(--sidebar-border);
    }

    .sidebar-app-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: var(--accent);
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.1rem;
    }

    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-dark) !important;
        text-align: center;
        margin: 0;
    }

    .sidebar-subtitle {
        font-size: 0.8rem;
        color: var(--text-muted) !important;
        letter-spacing: 0.05em;
        text-align: center;
        margin: 0;
    }

    .scenario-card {
        background: #ffffff;
        border: 1px solid var(--sidebar-border);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }

    .scenario-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted) !important;
        margin: 0.3rem 0 0.7rem;
        padding: 0 0.5rem;
        font-weight: 600;
        text-align: center;
    }

    /* Custom navigation menu items */
    .nav-menu-container {
        display: none;
    }

    .nav-menu-btn {
        display: none;
    }

    .aadhaar-logo {
        width: 90px;
        height: 90px;
        margin: 0.8rem auto 0.6rem;
        display: block;
        object-fit: contain;
    }

    /* Wrapper for logo to ensure centering */
    [data-testid="stSidebar"] img.aadhaar-logo {
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Sidebar navigation: full-width stacked bars */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0;
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    [data-testid="stSidebar"] label[data-baseweb="radio"] {
        /* stretch to the sidebar edges, ignoring sidebar padding */
        width: 100%;
        max-width: 100% !important;
        margin-left: 0;
        display: flex;
        align-items: center;
        padding: 0.9rem 0.85rem;
        margin: 0;
        border-radius: 0;
        background: var(--sidebar-bg);
        border: none;
        border-bottom: 1px solid var(--sidebar-border);
        cursor: pointer;
        user-select: none;
    }

    [data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
        background: var(--sidebar-hover);
    }

    /* Hide the radio dot */
    [data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child {
        display: none;
    }

    /* Style for navigation icons */
    [data-testid="stSidebar"] .nav-icon {
        margin-right: 0.75rem;
        font-size: 1.1rem;
        color: var(--text-muted);
        transition: color 0.2s ease;
    }

    /* Change icon color when selected */
    [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) .nav-icon {
        color: #ffffff;
    }

    /* Ensure label text shows fully */
    [data-testid="stSidebar"] label[data-baseweb="radio"] * {
        white-space: nowrap;
    }

    /* Selected state: accent background with white text */
    [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
        background: var(--accent);
        border-color: var(--accent);
    }

    [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) * {
        color: #ffffff !important;
        font-weight: 600;
    }

    .nav-button {
        display: block;
        width: 100%;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border: 2px solid transparent;
        border-radius: 8px;
        background: #f1f5f9;
        color: var(--text-muted);
        text-align: left;
        font-weight: 500;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
    }

    .nav-button:hover {
        background: rgba(245, 158, 11, 0.1);
        border-color: rgba(245, 158, 11, 0.3);
        color: var(--accent);
    }

    .nav-button.active {
        background: rgba(245, 158, 11, 0.15);
        border-color: var(--accent);
        color: var(--accent);
        font-weight: 600;
    }

    .nav-icon {
        margin-right: 0.6rem;
        font-size: 1.1rem;
    }

    .nav-menu {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .nav-menu-item {
        display: flex;
        align-items: center;
        width: 100%;
        padding: 0.9rem 1.2rem;
        border: none;
        border-radius: 8px;
        background: #f1f5f9;
        color: var(--text-muted);
        text-align: left;
        font-weight: 500;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.25s ease;
        font-family: 'Inter', sans-serif;
        margin-bottom: 0.5rem;
    }

    .nav-menu-item:hover {
        background: #e2e8f0;
    }

    .nav-menu-item.active {
        background: var(--accent);
        color: #ffffff;
        font-weight: 600;
    }

    .nav-menu-icon {
        font-size: 1.3rem;
        margin-right: 1rem;
        min-width: 24px;
        display: flex;
        align-items: center;
    }

    /* SAC components - use default light styling */
    [data-testid="stSidebar"] .ant-menu-item-selected,
    [data-testid="stSidebar"] .ant-menu-item-selected:hover {
        background: rgba(245, 158, 11, 0.15) !important;
        color: var(--accent) !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] .ant-menu-submenu-title:hover,
    [data-testid="stSidebar"] .ant-menu-item:hover {
        background: var(--sidebar-hover) !important;
        color: var(--accent) !important;
    }

    [data-testid="stSidebar"] .ant-tag {
        background: rgba(245, 158, 11, 0.12) !important;
        color: var(--accent) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    [data-testid="stSidebar"] .ant-cascader-picker {
        background: #ffffff !important;
        border: 1px solid var(--sidebar-border) !important;
        border-radius: 10px !important;
        padding: 0.35rem 0.65rem !important;
    }

    [data-testid="stSidebar"] .ant-cascader-picker:hover,
    [data-testid="stSidebar"] .ant-cascader-picker-focused {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2) !important;
    }

    .toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.2rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid var(--divider);
    }

    .toolbar-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-dark);
        letter-spacing: 0.02em;
    }

    .toolbar-subtitle {
        font-size: 0.8rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-top: 0.3rem;
    }

    .stButton>button {
        background: var(--accent);
        color: #1c1f23;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        box-shadow: none;
    }

    .stButton>button:hover {
        background: var(--accent-dark);
    }

    .metric-card {
        background: var(--card-bg);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        color: var(--text-dark);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent);
        border-bottom: 3px solid var(--accent);
    }
</style>
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
    # ZONE 3: ADMINISTRATIVE FILTERS (sac.cascader)
    # State > District > Block hierarchy
    # ==========================================
    st.markdown("<div class='scenario-label'>Administrative Filter</div>", unsafe_allow_html=True)
    
    admin_hierarchy = [
        sac.CasItem(
            "Jharkhand",
            icon="geo-alt",
            children=[
                sac.CasItem(
                    "Ranchi",
                    children=[
                        sac.CasItem("Kanke"),
                        sac.CasItem("Ratu"),
                        sac.CasItem("Bundu"),
                    ],
                ),
                sac.CasItem(
                    "Hazaribagh",
                    children=[
                        sac.CasItem("Sadar"),
                        sac.CasItem("Ichak"),
                        sac.CasItem("Katkamsandi"),
                    ],
                ),
                sac.CasItem(
                    "Giridih",
                    children=[
                        sac.CasItem("Dumri"),
                        sac.CasItem("Pirtand"),
                        sac.CasItem("Bagodar"),
                    ],
                ),
            ],
        ),
    ]
    
    # Get default admin selection from session state
    default_admin_index = st.session_state.get("admin_filter_index", [0, 0, 0])
    
    admin_selection = sac.cascader(
        items=admin_hierarchy,
        index=default_admin_index,
        placeholder="Select State > District > Block",
        color="#f59e0b",
        search=True,
        clear=True,
        return_index=True,
        key="admin_filter_selector",
    )
    
    if admin_selection:
        st.session_state.admin_filter_index = admin_selection
    
    st.divider()
    
    # ==========================================
    # ZONE 4: OPTIMIZATION POLICY CONTROL
    # Technical differentiator - exposes cost vs equity trade-offs
    # ==========================================
    st.markdown("<div class='scenario-label'>Optimization Priority</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="
            background: #ffffff;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin: 0 0.5rem 0.75rem;
            border: 1px solid #e2e8f0;
        ">
            <div style="
                font-size: 0.75rem;
                color: #64748b;
                line-height: 1.4;
            ">
                Toggle between minimizing operational cost or maximizing student inclusion
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize policy mode in session state
    if 'policy_mode' not in st.session_state:
        st.session_state.policy_mode = "balanced"
    
    # Enterprise-grade segmented control using SAC
    policy_mode = sac.segmented(
        items=[
            sac.SegmentedItem(label="⚡ Efficiency", icon="lightning-charge"),
            sac.SegmentedItem(label="⚖️ Balanced", icon="sliders"),
            sac.SegmentedItem(label="🎯 Equity", icon="heart"),
        ],
        index={"efficiency": 0, "balanced": 1, "equity": 2}.get(st.session_state.policy_mode, 1),
        color="#f59e0b",
        size="sm",
        radius="lg",
        use_container_width=True,
        key="policy_mode_selector",
    )
    
    # Map selection to mode
    policy_mode_map = {0: "efficiency", 1: "balanced", 2: "equity"}
    if policy_mode is not None:
        st.session_state.policy_mode = policy_mode_map.get(policy_mode, "balanced")
    
    current_mode = st.session_state.policy_mode
    
    # Policy mode info cards
    mode_info = {
        "efficiency": {
            "title": "Efficiency Mode",
            "subtitle": "Minimize Cost",
            "desc": "Optimizes for shortest routes and lowest fuel consumption. Urban-centric coverage.",
            "color": "#3b82f6",
            "icon": "⚡",
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
            "icon": "⚖️",
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
            "icon": "🎯",
            "cost_impact": "HIGHER",
            "equity_impact": "MAXIMUM",
            "cost_color": "#f59e0b",
            "equity_color": "#22c55e",
        },
    }
    
    info = mode_info.get(current_mode, mode_info["balanced"])
    
    st.markdown(f"""
        <div style="
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid {info['color']};
            border-radius: 10px;
            padding: 1rem;
            margin-top: 0.75rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.1rem;">{info['icon']}</span>
                <div>
                    <div style="font-size: 0.85rem; font-weight: 700; color: #1e293b;">{info['title']}</div>
                    <div style="font-size: 0.7rem; color: {info['color']}; font-weight: 600;">{info['subtitle']}</div>
                </div>
            </div>
            <div style="font-size: 0.75rem; color: #64748b; line-height: 1.4; margin-bottom: 0.75rem;">
                {info['desc']}
            </div>
            <div style="display: flex; gap: 0.75rem;">
                <div style="
                    flex: 1;
                    background: #f8fafc;
                    border-radius: 6px;
                    padding: 0.5rem;
                    text-align: center;
                ">
                    <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">Fuel Cost</div>
                    <div style="font-size: 0.75rem; font-weight: 700; color: {info['cost_color']};">{info['cost_impact']}</div>
                </div>
                <div style="
                    flex: 1;
                    background: #f8fafc;
                    border-radius: 6px;
                    padding: 0.5rem;
                    text-align: center;
                ">
                    <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">Equity</div>
                    <div style="font-size: 0.75rem; font-weight: 700; color: {info['equity_color']};">{info['equity_impact']}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Scenario Planning Expander
    with st.expander("Scenario Planning", expanded=True):
        st.markdown("<div class='scenario-label'>Mission Focus</div>", unsafe_allow_html=True)

        focus_items = [
            sac.CasItem(
                "Mission Intensity",
                children=[
                    sac.CasItem("Backlog Surge"),
                    sac.CasItem("Access Equity Sweep"),
                ],
            ),
            sac.CasItem(
                "Calendar Sensitivity",
                children=[
                    sac.CasItem("Board Exam Critical"),
                    sac.CasItem("Seasonal Disruption"),
                ],
            ),
        ]

        def _labels_from_index(items_list, index_path):
            labels = []
            branch = items_list
            if not index_path:
                return labels

            def _extract(node, key):
                if isinstance(node, dict):
                    return node.get(key)
                return getattr(node, key, None)

            for idx in index_path:
                if not branch or idx < 0 or idx >= len(branch):
                    break
                node = branch[idx]
                label = _extract(node, "label")
                if label:
                    labels.append(label)
                children = _extract(node, "children")
                branch = children or []
            return labels

        default_focus_index = st.session_state.get("mission_focus_index", [0, 0])

        focus_selection = sac.cascader(
            items=focus_items,
            index=default_focus_index,
            placeholder="Select deployment focus",
            color="#ffcb05",
            search=True,
            clear=True,
            return_index=True,
            key="mission_focus_selector",
        )

        if focus_selection:
            st.session_state.mission_focus_index = focus_selection
            mission_focus_path = _labels_from_index(focus_items, focus_selection)
        else:
            mission_focus_path = _labels_from_index(focus_items, default_focus_index)

        if not mission_focus_path:
            mission_focus_path = ["Mission Intensity", "Backlog Surge"]

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
    
    # Status panel
    st.markdown("<div class='scenario-label'>System Status</div>", unsafe_allow_html=True)
    col_status1, col_status2 = st.columns(2)
    with col_status1:
        st.metric("Version", "2.0.1")
    with col_status2:
        st.metric("Status", "Active")

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
