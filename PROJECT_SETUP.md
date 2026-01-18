# Vidyarthi-Raksha: Modern Digital Administration Dashboard

A Streamlit-based logistics optimization dashboard for Aadhaar enrollment and biometric update management. Built with the UX4G (Modern Digital Administration) color palette and govtech branding.

## Project Structure

```
Vidyarthi-Raksha/
├── core/                          # Core utilities and configuration
│   ├── __init__.py
│   └── constants.py              # UX4G palette, app metadata, settings
├── ui/                            # UI & styling components
│   ├── __init__.py
│   └── styling.py                # apply_govtech_theme() function
├── views/                         # Page layouts and views
│   └── __init__.py
├── assets/                        # Static resources
│   └── css/                       # Custom CSS (if needed)
├── data/                          # Data files and datasets
│   └── (mock_school_data.csv, aadhaar data, etc.)
├── app.py                         # Main Streamlit application
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## UX4G Color Palette

| Color | Hex Code | Usage |
|-------|----------|-------|
| **Saffron (Primary)** | #FF9933 | Buttons, accents, metric card borders |
| **Green (Secondary)** | #138808 | Success states, confirmations |
| **Deep Blue (Neutral)** | #000080 | Sidebar, primary backgrounds |
| **Red (Risk)** | #DC3545 | Alerts, critical states, warnings |

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### 3. Using the GovTech Theme

In your main `app.py`:

```python
import streamlit as st
from ui.styling import apply_govtech_theme
from core.constants import APP_TITLE, APP_VERSION

# Apply the theme first
apply_govtech_theme()

st.set_page_config(
    page_title=f"{APP_TITLE} | Command Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Your app content here
```

## Key Features

### 1. Core Module (`core/constants.py`)
- **Color Palette**: Pre-defined UX4G colors
- **Typography**: Font sizes and family stack
- **Spacing**: Border radius and shadow constants
- **Metadata**: App title, version, ministry name

### 2. UI Module (`ui/styling.py`)
- **`apply_govtech_theme()`**: Injects comprehensive CSS for govtech aesthetic
  - Saffron accents for primary actions
  - Deep blue sidebar with white text
  - Metric cards with left-border styling (5px saffron)
  - Inter/Roboto font stack
  - Smooth transitions and hover effects

- **`get_color_by_status(status)`**: Returns appropriate color based on state
- **`create_metric_html(label, value, unit)`**: Generates styled metric card HTML

### 3. Metric Cards

Metric cards automatically include:
- White background
- 1px divider border
- **5px saffron left-border** (#FF9933)
- Subtle box shadow with hover lift effect
- Responsive typography

### 4. Sidebar Styling

The sidebar enforces:
- Deep blue (#000080) background
- White text
- Transparent white input fields with saffron focus states
- Proper contrast for accessibility

## Customization

### Modify Colors

Edit `core/constants.py`:

```python
COLOR_PRIMARY = "#FF9933"      # Change Saffron
COLOR_SECONDARY = "#138808"    # Change Green
COLOR_NEUTRAL = "#000080"      # Change Deep Blue
COLOR_RISK_HIGH = "#DC3545"    # Change Red
```

### Add Custom CSS

The `apply_govtech_theme()` function returns a comprehensive CSS string. Extend it by:

1. Adding CSS in the `<style>` block in `ui/styling.py`
2. Or creating custom stylesheets in `assets/css/` and importing them

### Use Metric Helper

```python
from ui.styling import create_metric_html

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(create_metric_html("Total Backlog", "5,234", "students"), 
                unsafe_allow_html=True)
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.28.1 | Web app framework |
| pandas | 2.1.3 | Data manipulation |
| pydeck | 0.8.1 | Map visualization |
| plotly | 5.17.0 | Interactive charts |
| scikit-learn | 1.3.2 | ML & optimization |
| streamlit-antd-components | 0.2.2 | Ant Design UI components |
| ortools | 9.8.3296 | Vehicle routing optimization |

## Operational Settings

Key configuration values in `core/constants.py`:

- **Default Mobile Vans**: 3
- **Default Daily Capacity**: 150 updates/van
- **Max Mobile Vans**: 10
- **Supported Languages**: English, हिन्दी, ಕನ್ನಡ, தமிழ್

## Ministry Branding

- **App Title**: Vidyarthi-Raksha
- **Dashboard Type**: Command Centre Dashboard
- **Version**: 2.0.1
- **Ministry**: Ministry of Rural Development

## Next Steps

**Phase 2: View Components** — Create reusable view components for metrics, maps, and filters.

**Phase 3: Data Integration** — Connect to live data sources and implement caching.

**Phase 4: Route Optimization** — Integrate OR-Tools for vehicle routing problem solving.

---

**Built for**: Modern Digital Administration Initiative (UX4G)  
**Last Updated**: January 2026
