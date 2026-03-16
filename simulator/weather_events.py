"""
TerraSensus — Weather Event Models

Standalone module for weather event logic — decoupled from the simulator
so it can be tested independently and reused by the drought risk service.
"""

from dataclasses import dataclass
from enum import Enum


class EventType(str, Enum):
    RAIN = "rain"
    DROUGHT = "drought"
    HEATWAVE = "heatwave"


@dataclass
class WeatherEvent:
    event_type: EventType
    duration_hours: float
    intensity: float       # 0.0–1.0, scales the effect magnitude
    description: str


def rain_event(moisture_spike_pct: float, duration_hours: float = 2.0) -> WeatherEvent:
    return WeatherEvent(
        event_type=EventType.RAIN,
        duration_hours=duration_hours,
        intensity=moisture_spike_pct / 20.0,
        description=f"Rain event — moisture spike +{moisture_spike_pct:.1f}%",
    )


def drought_event(days_without_rain: float) -> WeatherEvent:
    intensity = min(1.0, (days_without_rain - 14) / 30)  # ramps up after 14 days
    return WeatherEvent(
        event_type=EventType.DROUGHT,
        duration_hours=days_without_rain * 24,
        intensity=intensity,
        description=f"Drought — {days_without_rain:.0f} days without rain, intensity {intensity:.2f}",
    )


def heatwave_event(temp_increase: float, duration_hours: float = 48.0) -> WeatherEvent:
    return WeatherEvent(
        event_type=EventType.HEATWAVE,
        duration_hours=duration_hours,
        intensity=temp_increase / 10.0,
        description=f"Heatwave — +{temp_increase:.1f}°C for {duration_hours:.0f}h",
    )
