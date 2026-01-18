"""
Data module for Vidyarthi-Raksha
Contains digital twin datasets and precomputed scenarios.
"""

from .precomputed_scenarios import (
    get_scenario_cache,
    generate_demo_routes,
    generate_mobile_unit_positions,
    get_hexagon_data,
    ScenarioCache,
)

__all__ = [
    'get_scenario_cache',
    'generate_demo_routes',
    'generate_mobile_unit_positions',
    'get_hexagon_data',
    'ScenarioCache',
]
