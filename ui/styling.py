"""
GovTech Theme & Styling Module
Applies the Modern Digital Administration (UX4G) aesthetic to Streamlit
"""

import streamlit as st
from core.constants import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_NEUTRAL, COLOR_RISK_HIGH,
    COLOR_NEUTRAL_LIGHT, COLOR_TEXT_DARK, COLOR_TEXT_MUTED, COLOR_DIVIDER,
    FONT_FAMILY, BORDER_RADIUS_SM, BORDER_RADIUS_MD, BORDER_RADIUS_LG,
    METRIC_CARD_BORDER_LEFT, SHADOW_MD
)


def apply_govtech_theme():
    """
    Applies the UX4G govtech theme to the Streamlit application.
    
    Features:
    - Saffron (#FF9933) accents for primary actions
    - Deep blue (#000080) sidebar with white text
    - Metric cards with left-border saffron styling
    - Inter/Roboto font stack for modern appearance
    - Subtle shadows and smooth transitions
    - Professional spacing and alignment
    """
    
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Roboto:wght@400;500;700&display=swap');

        :root {{
            --color-primary: {COLOR_PRIMARY};
            --color-secondary: {COLOR_SECONDARY};
            --color-neutral: {COLOR_NEUTRAL};
            --color-risk-high: {COLOR_RISK_HIGH};
            --color-neutral-light: {COLOR_NEUTRAL_LIGHT};
            --color-text-dark: {COLOR_TEXT_DARK};
            --color-text-muted: {COLOR_TEXT_MUTED};
            --color-divider: {COLOR_DIVIDER};
            --font-family: {FONT_FAMILY};
        }}

        * {{
            font-family: var(--font-family);
        }}

        body, .main {{
            background: var(--color-neutral-light);
            color: var(--color-text-dark);
        }}

        .block-container {{
            padding: 1.25rem 2.2rem 2.5rem;
            max-width: 100%;
        }}

        /* ==========================================
           SIDEBAR STYLING
           ========================================== */
        [data-testid="stSidebar"] {{
            background: var(--color-neutral);
            border-right: 1px solid rgba(0, 0, 0, 0.2);
            min-width: 270px;
            padding: 1.5rem 1.3rem 2rem;
        }}

        [data-testid="stSidebar"] * {{
            color: #ffffff !important;
        }}

        [data-testid="stSidebar"] .stTextInput input,
        [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {{
            background: rgba(255, 255, 255, 0.12) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: #ffffff !important;
        }}

        [data-testid="stSidebar"] .stTextInput input::placeholder {{
            color: rgba(255, 255, 255, 0.6) !important;
        }}

        [data-testid="stSidebar"] .stTextInput input:focus,
        [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"]:focus-within {{
            border-color: var(--color-primary) !important;
            box-shadow: 0 0 0 2px rgba(255, 153, 51, 0.25) !important;
        }}

        /* ==========================================
           METRIC CARDS
           ========================================== */
        .metric-card {{
            background: #ffffff;
            border: 1px solid var(--color-divider);
            border-left: {METRIC_CARD_BORDER_LEFT} solid var(--color-primary);
            border-radius: {BORDER_RADIUS_LG};
            padding: 1rem 1.2rem;
            box-shadow: {SHADOW_MD};
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            transition: all 0.3s ease;
        }}

        .metric-card:hover {{
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }}

        .metric-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--color-text-muted);
            font-weight: 600;
        }}

        .metric-value {{
            font-size: 1.85rem;
            font-weight: 700;
            color: var(--color-text-dark);
            line-height: 1.2;
        }}

        /* ==========================================
           BUTTONS & ACTIONS
           ========================================== */
        .stButton > button {{
            background: var(--color-primary);
            color: #ffffff;
            border-radius: {BORDER_RADIUS_SM};
            border: none;
            padding: 0.5rem 1.2rem;
            font-weight: 600;
            box-shadow: none;
            transition: all 0.2s ease;
        }}

        .stButton > button:hover {{
            background: #E67E22;
            box-shadow: {SHADOW_MD};
        }}

        .stButton > button:focus {{
            outline: none;
            box-shadow: 0 0 0 3px rgba(255, 153, 51, 0.25);
        }}

        /* ==========================================
           FORM INPUTS & SELECTORS
           ========================================== */
        .stSelectbox label,
        .stNumberInput label,
        .stTextInput label {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--color-text-muted);
            font-weight: 600;
        }}

        .stSelectbox [data-baseweb="select"],
        .stNumberInput input,
        .stTextInput > div > div > input {{
            border-radius: {BORDER_RADIUS_SM};
            border: 1px solid var(--color-divider);
            background: #ffffff;
            color: var(--color-text-dark);
            font-size: 0.9rem;
        }}

        .stSelectbox [data-baseweb="select"]:focus-within,
        .stNumberInput input:focus,
        .stTextInput > div > div > input:focus {{
            border-color: var(--color-primary);
            box-shadow: 0 0 0 2px rgba(255, 153, 51, 0.25);
        }}

        /* ==========================================
           TABS
           ========================================== */
        .stTabs [data-baseweb="tab-list"] {{
            border-bottom: 1px solid var(--color-divider);
            background: #ffffff;
            padding: 0 0.2rem;
            gap: 0.1rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 0;
            padding: 0.65rem 1.1rem;
            font-weight: 600;
            font-size: 0.92rem;
            color: var(--color-text-muted);
            border-bottom: 3px solid transparent;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            color: var(--color-text-dark);
        }}

        .stTabs [aria-selected="true"] {{
            color: var(--color-text-dark) !important;
            border-bottom: 3px solid var(--color-primary) !important;
        }}

        /* ==========================================
           CARDS & CONTAINERS
           ========================================== */
        .card {{
            background: #ffffff;
            border: 1px solid var(--color-divider);
            border-radius: {BORDER_RADIUS_LG};
            padding: 1.2rem;
            box-shadow: {SHADOW_MD};
        }}

        /* ==========================================
           DATAFRAME STYLING
           ========================================== */
        .stDataFrame {{
            border-radius: {BORDER_RADIUS_LG};
            border: 1px solid var(--color-divider);
            background: #ffffff;
        }}

        /* ==========================================
           ALERTS & MESSAGES
           ========================================== */
        .stAlert {{
            border-radius: {BORDER_RADIUS_MD};
            border-left: 4px solid var(--color-primary);
        }}

        .stWarning {{
            border-left-color: var(--color-risk-high) !important;
        }}

        .stSuccess {{
            border-left-color: var(--color-secondary) !important;
        }}

        /* ==========================================
           FOOTER & BRANDING
           ========================================== */
        footer {{
            background: var(--color-neutral);
            color: #ffffff;
            border-radius: {BORDER_RADIUS_LG};
            padding: 2rem;
            text-align: center;
            font-size: 0.85rem;
        }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def get_color_by_status(status):
    """
    Returns appropriate UX4G color based on status/state.
    
    Args:
        status (str): One of 'primary', 'secondary', 'success', 'risk', 'neutral'
    
    Returns:
        str: Hex color code
    """
    status_map = {
        'primary': COLOR_PRIMARY,
        'secondary': COLOR_SECONDARY,
        'success': COLOR_SECONDARY,
        'risk': COLOR_RISK_HIGH,
        'neutral': COLOR_TEXT_MUTED,
    }
    return status_map.get(status.lower(), COLOR_NEUTRAL)


def create_metric_html(label, value, unit=""):
    """
    Creates an HTML snippet for a metric card.
    
    Args:
        label (str): Metric label (e.g., "Total Backlog")
        value (str/int): Metric value
        unit (str): Optional unit (e.g., "students", "days")
    
    Returns:
        str: HTML markup for metric card
    """
    unit_str = f"<span style='font-size: 0.75rem; color: var(--color-text-muted);'>{unit}</span>" if unit else ""
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {unit_str}
    </div>
    """
