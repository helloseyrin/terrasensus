"""
TerraSensus — Alert Threshold Rules

Global thresholds apply when no crop-specific override exists.
Crop overrides reflect agronomic reality — a vineyard and a wheat field
have fundamentally different nutrient requirements.

IMPORTANT: Do not change threshold values without agronomic justification
and updating the corresponding test in tests/test_rules.py and CLAUDE.md.
All values require domain expert validation before production use.
"""

# Global defaults — apply when crop is unknown or has no override
THRESHOLDS = {
    "moisture":    {"critical_low": 10,   "low": 20,  "high": 80,   "critical_high": 90,  "unit": "%"},
    "temperature": {"critical_low": 2,    "low": 5,   "high": 30,   "critical_high": 35,  "unit": "°C"},
    "ph":          {"critical_low": 5.0,  "low": 5.5, "high": 7.5,  "critical_high": 8.5, "unit": ""},
    "nitrogen":    {"critical_low": 15,   "low": 30,  "high": 150,  "critical_high": 180, "unit": "mg/kg"},
    "phosphorus":  {"critical_low": 10,   "low": 20,  "high": 80,   "critical_high": 120, "unit": "mg/kg"},
    "potassium":   {"critical_low": 40,   "low": 80,  "high": 200,  "critical_high": 250, "unit": "mg/kg"},
    "ec":          {"critical_low": 0.1,  "low": 0.2, "high": 2.0,  "critical_high": 3.0, "unit": "dS/m"},
}

# Crop-specific overrides
# Only override sensors where the crop genuinely differs from global defaults.
# All values flagged ⚠ UNVALIDATED — require agronomist review before production.
CROP_THRESHOLDS: dict[str, dict] = {

    "wheat": {
        # Winter wheat — Triticum aestivum. Continental climate (Ukraine chernozem baseline).
        # Heavy N feeder. Alkaline-tolerant. Moderate EC tolerance.
        "ph":       {"critical_low": 5.5, "low": 6.0, "high": 7.5, "critical_high": 8.0, "unit": ""},
        "nitrogen": {"critical_low": 20,  "low": 50,  "high": 160, "critical_high": 200, "unit": "mg/kg"},
        "ec":       {"critical_low": 0.1, "low": 0.3, "high": 2.5, "critical_high": 3.5, "unit": "dS/m"},
        # ⚠ UNVALIDATED — based on general wheat agronomy literature
    },

    "cotton": {
        # Gossypium hirsutum — arid region (Uzbekistan). Salt-tolerant crop.
        # Higher EC tolerance than most crops (hence the Aral Sea disaster —
        # cotton survived the saline conditions that killed everything else).
        # Needs warm soil. Low N relative to wheat. Alkaline soil tolerance.
        "ph":          {"critical_low": 5.8, "low": 6.5, "high": 8.0, "critical_high": 8.5, "unit": ""},
        "nitrogen":    {"critical_low": 10,  "low": 30,  "high": 100, "critical_high": 130, "unit": "mg/kg"},
        "temperature": {"critical_low": 12,  "low": 18,  "high": 38,  "critical_high": 42,  "unit": "°C"},
        "ec":          {"critical_low": 0.1, "low": 0.5, "high": 3.5, "critical_high": 5.0, "unit": "dS/m"},
        # ⚠ UNVALIDATED — cotton EC tolerance is well-documented but specific
        # mg/kg values need Central Asian agronomist review
    },

    "pinot_noir": {
        # Vitis vinifera — maritime climate (Willamette Valley, Oregon).
        # Grapes are deliberately kept N-low: excess N drives vegetative growth
        # at the expense of fruit quality and sugar concentration.
        # Prefer slightly acidic soils (volcanic Jory loam).
        # Low EC — grapes are more salt-sensitive than field crops.
        "ph":       {"critical_low": 5.0, "low": 5.5, "high": 6.8, "critical_high": 7.5, "unit": ""},
        "nitrogen": {"critical_low": 10,  "low": 15,  "high": 60,  "critical_high": 90,  "unit": "mg/kg"},
        "potassium":{"critical_low": 60,  "low": 100, "high": 220, "critical_high": 280, "unit": "mg/kg"},
        "ec":       {"critical_low": 0.1, "low": 0.2, "high": 1.5, "critical_high": 2.0, "unit": "dS/m"},
        # ⚠ UNVALIDATED — viticulture N values particularly need expert review.
        # Pinot Noir is especially sensitive to N management; numbers here are
        # conservative estimates from Oregon extension service literature.
    },

    # Add new crops here following the same pattern.
    # Only override sensors where this crop differs from global THRESHOLDS.
    # Always add an ⚠ UNVALIDATED comment until reviewed by a domain expert.
}


def get_thresholds(crop: str | None = None) -> dict:
    """
    Return merged threshold dict for a given crop.
    Crop overrides are applied on top of global defaults.
    """
    base = dict(THRESHOLDS)
    if crop and crop in CROP_THRESHOLDS:
        for sensor, values in CROP_THRESHOLDS[crop].items():
            base[sensor] = values
    return base


def evaluate(sensor: str, value: float, crop: str | None = None) -> dict | None:
    """
    Evaluate a sensor reading against crop-aware thresholds.
    Returns an alert dict if outside healthy range, None otherwise.

    Args:
        sensor: sensor name (moisture, ph, nitrogen, etc.)
        value:  current reading
        crop:   crop type from plot config (optional — uses global if None)

    Returns:
        {sensor, value, level, direction, unit, crop} or None
    """
    thresholds = get_thresholds(crop)
    t = thresholds.get(sensor)
    if not t:
        return None

    if value <= t["critical_low"] or value >= t["critical_high"]:
        level = "critical"
    elif value <= t["low"] or value >= t["high"]:
        level = "warning"
    else:
        return None

    direction = "low" if value <= t["low"] else "high"
    return {
        "sensor": sensor,
        "value": value,
        "level": level,
        "direction": direction,
        "unit": t["unit"],
        "crop": crop or "global",
    }
