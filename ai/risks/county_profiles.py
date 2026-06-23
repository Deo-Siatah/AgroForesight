"""
County-level normalization.

Dry counties should not automatically
appear riskier than high-rainfall counties.
"""

COUNTY_RISK_MULTIPLIERS = {
    "Mandera": 0.80,
    "Wajir": 0.85,
    "Marsabit": 0.85,
    "Turkana": 0.80,
    "Garissa": 0.90,

    "Nakuru": 1.00,
    "Trans Nzoia": 1.00,
    "Uasin Gishu": 1.00,
    "Kericho": 1.00,
    "Bungoma": 1.00,

    "Kisumu": 1.05,
    "Busia": 1.05,
}

DEFAULT_MULTIPLIER = 1.00