"""
TerraSensus — Drought Risk Module

Combines Open-Meteo historical rainfall data with soil moisture trends
to produce a drought risk score (0.0 = no risk, 1.0 = critical drought).
"""
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Thresholds for drought scoring
RAINFALL_DEFICIT_THRESHOLD_MM = 20  # less than 20mm in 30 days = at risk
MOISTURE_DECLINE_THRESHOLD = 5      # moisture dropped >5% over 7 days = at risk


def get_rainfall_last_30d(latitude: float, longitude: float) -> float:
    """Fetch cumulative rainfall (mm) for the past 30 days from Open-Meteo."""
    # TODO: implement Open-Meteo historical API call
    raise NotImplementedError


def calculate_drought_risk(
    latitude: float,
    longitude: float,
    moisture_readings: list[float],  # last 7 days, oldest first
) -> dict:
    """
    Returns drought risk assessment dict:
    {
        "risk_score": float,         # 0.0–1.0
        "risk_level": str,           # "low" | "moderate" | "high" | "critical"
        "rainfall_30d_mm": float,
        "moisture_7d_delta": float,
        "recommendation": str,
    }
    """
    # TODO: implement scoring logic
    raise NotImplementedError
