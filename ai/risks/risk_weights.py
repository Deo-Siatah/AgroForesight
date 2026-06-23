"""
Centralized risk weight configuration.

All scoring caps live here.
Changing business risk appetite should only require
modifying values in this file.
"""

MAX_WEATHER_RISK = 25

MAX_SEASON_RISK = 20

MAX_HARVEST_RISK = 20

MAX_FINANCIAL_RISK = 20

MAX_FARMER_RISK = 15

TOTAL_MAX_RISK = (
    MAX_WEATHER_RISK
    + MAX_SEASON_RISK
    + MAX_HARVEST_RISK
    + MAX_FINANCIAL_RISK
    + MAX_FARMER_RISK
)