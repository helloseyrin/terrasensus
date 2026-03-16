# Engineering Notes — Sensor Simulation

Key insights and design decisions captured during development.
These complement the ADRs (which cover *what* was decided) by explaining *why* things work the way they do.

---

## Realistic drift modelling

Real IoT soil sensors don't produce clean, stable values. They exhibit three distinct behaviours that must each be modelled separately:

1. **Slow drift** — moisture evaporates over hours; nutrients deplete slowly over days. Modelled as a `drift_per_hour` rate applied each tick.
2. **Stochastic events** — rain spikes moisture suddenly; heatwaves spike temperature. Modelled as probabilistic events in `weather_events.py` with configurable `probability_per_hour`.
3. **Gaussian noise** — every sensor reading has measurement imprecision. Modelled as `value + random.gauss(0, sigma)` on every reading.

Separating these three concerns makes each independently testable and configurable in `config.yaml`.

**Why it matters for the alert engine**: a simulator that only adds noise will never trigger a "moisture critically low" alert. Drift is what creates the scenarios that stress-test your threshold rules.

---

## Diurnal temperature cycle

Soil temperature does not drift linearly — it follows a daily sinusoidal cycle: warmest at ~14:00, coolest at ~04:00. The simulator uses:

```python
5.0 * math.sin(math.pi * (hour - 4) / 12)
```

This gives a ±5°C swing around the baseline, which is agronomically realistic for temperate climates.

---

## Floor/ceiling clamping

All sensor values are clamped to physical limits (`min`/`max` in `config.yaml`) after noise is applied. Without this, a low-moisture plot running for days will eventually produce negative moisture values, which would confuse the alert engine and corrupt dashboard charts.

---

## Phase 2: PySensorMQTT

In phase 2, `sensor_simulator.py` will be replaced by **PySensorMQTT** — a Python library for reading real soil sensor data over MQTT. The simulator's output schema (the `reading` dict) is deliberately identical to what a real MQTT sensor would publish, so the ingestion service requires no changes when switching. This is an intentional design constraint: keep the simulator as a drop-in stand-in for real hardware.

MQTT topic structure (planned):
```
terrasensus/farms/{farm_id}/plots/{plot_id}/sensors/{sensor_name}
```

---

## Lab report simulation

The `lab_report_generator.py` uses `random.gauss(mean, std)` with agronomically validated distributions (sourced from USDA soil survey data) to generate PDF reports. This serves two purposes:

1. **Test fixtures** for the lab-parser service — you can generate 100 reports and run the parser against all of them without needing a real lab.
2. **Edge case generation** — occasionally a generated report will have extreme values (very low N, very high EC) that trigger alert rules. This is intentional.
