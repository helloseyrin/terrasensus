"""
TerraSensus — Alert Threshold Rules

All sensor thresholds are defined here as the single source of truth.
Values are agronomically validated — do not change without updating CLAUDE.md sensor table.
"""

THRESHOLDS = {
    "moisture": {"critical_low": 10, "low": 20, "high": 80, "critical_high": 90, "unit": "%"},
    "temperature": {"critical_low": 2, "low": 5, "high": 30, "critical_high": 35, "unit": "°C"},
    "ph": {"critical_low": 5.0, "low": 5.5, "high": 7.5, "critical_high": 8.5, "unit": ""},
    "nitrogen": {"critical_low": 15, "low": 30, "high": 150, "critical_high": 180, "unit": "mg/kg"},
    "phosphorus": {"critical_low": 10, "low": 20, "high": 80, "critical_high": 120, "unit": "mg/kg"},
    "potassium": {"critical_low": 40, "low": 80, "high": 200, "critical_high": 250, "unit": "mg/kg"},
    "ec": {"critical_low": 0.1, "low": 0.2, "high": 2.0, "critical_high": 3.0, "unit": "dS/m"},
}


def evaluate(sensor: str, value: float) -> dict:
    """Return alert level for a sensor reading. Returns None if within normal range."""
    t = THRESHOLDS.get(sensor)
    if not t:
        return None

    if value <= t["critical_low"] or value >= t["critical_high"]:
        level = "critical"
    elif value <= t["low"] or value >= t["high"]:
        level = "warning"
    else:
        return None

    direction = "low" if value <= t["low"] else "high"
    return {"sensor": sensor, "value": value, "level": level, "direction": direction, "unit": t["unit"]}
