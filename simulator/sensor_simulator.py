"""
TerraSensus — Sensor Simulator

Generates continuous, realistic soil sensor readings with:
  - Gaussian noise on every reading
  - Slow value drift over time (e.g. moisture evaporation)
  - Diurnal temperature cycle (warmer midday, cooler night)
  - Stochastic weather events (rain spikes, drought, heatwave)

Publishes JSON readings to GCP Pub/Sub on a configurable interval.
Phase 2: will be replaced by PySensorMQTT for real MQTT hardware integration.
"""

import json
import math
import random
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def diurnal_temperature_offset(hour: int) -> float:
    """Sinusoidal offset: warmest at 14:00, coolest at 04:00. Range ±5°C."""
    return 5.0 * math.sin(math.pi * (hour - 4) / 12)


def apply_noise(value: float, sigma: float) -> float:
    return value + random.gauss(0, sigma)


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


class PlotState:
    """Tracks the evolving sensor state for a single plot."""

    def __init__(self, plot_cfg: dict, sensor_cfg: dict):
        self.plot = plot_cfg
        self.sensors = sensor_cfg
        # Initialise current values at baseline
        self.values = {name: cfg["baseline"] for name, cfg in sensor_cfg.items()}
        self.hours_since_rain = 0.0
        self.active_events: list[dict] = []

    def tick(self, elapsed_hours: float) -> dict:
        """Advance state by elapsed_hours, return a reading dict."""
        now = datetime.now(timezone.utc)
        hour_of_day = now.hour

        # Apply drift to all sensors
        for name, cfg in self.sensors.items():
            drift = cfg["drift_per_hour"] * elapsed_hours

            # Temperature follows diurnal cycle instead of linear drift
            if name == "temperature":
                self.values[name] = cfg["baseline"] + diurnal_temperature_offset(hour_of_day)
            else:
                self.values[name] += drift

        self._process_events(elapsed_hours)
        self.hours_since_rain += elapsed_hours

        # Build reading with noise applied
        reading = {
            "plot_id": self.plot["id"],
            "plot_name": self.plot["name"],
            "latitude": self.plot["latitude"],
            "longitude": self.plot["longitude"],
            "crop": self.plot["crop"],
            "timestamp": now.isoformat(),
            "sensors": {},
        }

        for name, cfg in self.sensors.items():
            raw = apply_noise(self.values[name], cfg["noise_sigma"])
            reading["sensors"][name] = round(clamp(raw, cfg["min"], cfg["max"]), 3)

        return reading

    def _process_events(self, elapsed_hours: float):
        """Stochastic weather events modifying sensor state."""
        cfg = load_config()["weather_events"]

        # Rain event
        if random.random() < cfg["rain"]["probability_per_hour"] * elapsed_hours:
            spike = random.uniform(5, cfg["rain"]["moisture_spike"])
            self.values["moisture"] = clamp(
                self.values["moisture"] + spike,
                self.sensors["moisture"]["min"],
                self.sensors["moisture"]["max"],
            )
            self.hours_since_rain = 0
            logger.info(f"[{self.plot['id']}] Rain event — moisture +{spike:.1f}%")

        # Drought: accelerate moisture drift
        days_since_rain = self.hours_since_rain / 24
        if days_since_rain >= cfg["drought"]["trigger_days_no_rain"]:
            extra_drift = (
                self.sensors["moisture"]["drift_per_hour"]
                * (cfg["drought"]["drift_multiplier"] - 1)
                * elapsed_hours
            )
            self.values["moisture"] = clamp(
                self.values["moisture"] + extra_drift,
                self.sensors["moisture"]["min"],
                self.sensors["moisture"]["max"],
            )


def publish_reading(reading: dict, pubsub_topic: str):
    """
    Publish a sensor reading to GCP Pub/Sub.
    TODO: replace with real google-cloud-pubsub client.
    Currently logs to stdout for local development.
    """
    logger.info(f"PUBLISH → {pubsub_topic}: {json.dumps(reading)}")


def run():
    config = load_config()
    interval = config["publish"]["interval_seconds"]
    topic = config["publish"]["pubsub_topic"]
    elapsed_hours = interval / 3600

    plot_states = [
        PlotState(plot, config["sensors"])
        for plot in config["plots"]
    ]

    logger.info(f"TerraSensus simulator started — {len(plot_states)} plots, interval {interval}s")

    while True:
        for state in plot_states:
            reading = state.tick(elapsed_hours)
            publish_reading(reading, topic)
        time.sleep(interval)


if __name__ == "__main__":
    run()
