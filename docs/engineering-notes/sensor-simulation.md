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

## Simulation personas — why these three plots

The three plots in `config.yaml` are not arbitrary. Each is designed to exercise a specific scenario that a production system must handle correctly.

### Mykola Petrenko — Watermelon, Kherson Oblast, Ukraine (`plot-ukr-001`)
**Soil type**: Chernozem (black earth) — among the world's most fertile soils. High organic matter, naturally K-rich.
**Climate**: Continental — hot dry summers, cold winters. The hot dry continental summer is part of what makes Kherson watermelons exceptional: heat concentrates sugars, and the dry ripening period produces fruit with a flavour and sweetness that is genuinely distinctive.
**What this plot tests**:
- **N ceiling enforcement**: watermelon is a fruiting cucurbit — too much nitrogen drives vegetative vine growth at the expense of fruit sugar. The watermelon N critical_high (120 mg/kg) is well below the global default (180 mg/kg). A reading of 110 mg/kg is healthy globally but critical for this crop. This is the same false-alarm logic as Elena's low N, but in the opposite direction.
- **K floor for fruit quality**: potassium is the key nutrient for watermelon sweetness and flesh structure. The K low threshold (130 mg/kg) is higher than global (80 mg/kg) — K at 100 should trigger a warning even though global defaults say it's fine.
- **Cold soil sensitivity**: watermelons cannot be planted in cold soil and growth stalls below 16°C. Temperature thresholds alert much earlier than global defaults (critical_low=8°C vs global 2°C).
- **EC drift from irrigation**: starts at 0.8 dS/m and will creep up — tests slow EC escalation over a growing season

**Kherson Oblast context — design implications**:
Kherson city was de-occupied in November 2022. However, in June 2023 the Kakhovka dam was destroyed, flooding approximately 600,000 hectares of farmland on both banks of the Dnipro and contaminating soil with sewage, fuel, and unexploded ordnance residue — a deliberate act of ecocide affecting the most fertile agricultural land in Europe. Parts of the oblast remain contested. Farming continues on the right (Ukrainian-controlled) bank, but under conditions that make standard assumptions of precision agriculture (reliable internet, safe field access, functioning infrastructure) unreliable.

This has concrete implications for TerraSensus design:

- **Offline-first is not optional here.** In Oregon or even Uzbekistan, offline caching is a convenience. In Kherson, power and internet outages are routine. The rule-based alert engine must fire without network access. The mobile app must serve cached readings and recommendations with no connectivity. This is not a performance optimisation — it is a resilience requirement.
- **Remote monitoring matters more than field checks.** A farmer in Kherson may not be able to safely walk their plot to inspect crops. Sensor data viewed remotely (from shelter, from a different city, from abroad) may be the primary interaction mode. The UI must be legible on a phone under low-light conditions, under stress, with no time for tutorials.
- **Soil contamination beyond N-P-K.** Flooding from the dam destruction, fuel from military vehicles, and unexploded ordnance all affect soil chemistry in ways that go beyond TerraSensus's seven sensors. The app should not imply completeness — a damaged plot in Kherson may need heavy metal testing and contamination mapping that TerraSensus cannot provide. The agronomist disclaimer is especially important here.
- **We do not know the current ground truth.** Without direct contact with farmers currently operating in Kherson Oblast, TerraSensus's representation of this context is necessarily approximate. The simulation uses pre-2022 agronomic baselines. A farmer in this region today is dealing with realities that no soil model can accurately capture from the outside. If this app is ever deployed beyond demonstration, Kherson-region farmers must be involved in validating what the app shows and says about their land.

See `docs/personas.md` (Mykola section) for a full account of what is known, what is not known, and what this means for any future deployment in conflict-affected agricultural regions.

### Fatima Yusupova — Cotton, Ferghana Valley, Uzbekistan (`plot-uzb-001`)
**Soil type**: Serozem (grey desert soil) — thin, low organic matter, naturally alkaline.
**Climate**: Arid — extreme summer heat (40°C+), almost no rain, flood irrigation with saline water.
**What this plot tests**:
- **EC already in warning range at baseline** (2.4 dS/m): the system must fire a warning alert the first time it reads this plot, before any drift occurs
- **Cotton's higher EC tolerance**: global EC thresholds (critical_high=3.0) would over-alarm on cotton, which tolerates up to 5.0 dS/m. This persona is the primary test case for crop-aware EC thresholds
- Fast moisture drift (arid `moisture_drift_per_hour: -0.9`) — tests whether the alert engine fires irrigation alerts before the plot becomes critical
- Historical context: cotton monoculture + saline over-irrigation caused the Aral Sea disaster. This plot is deliberately set up to reproduce that scenario in simulation — the regenerative alternatives engine should recommend drip irrigation and salt-tolerant cover crops

### Elena Marchetti — Pinot Noir, Willamette Valley, Oregon (`plot-ore-001`)
**Soil type**: Jory silty clay loam — volcanic origin, iron-rich, excellent drainage.
**Climate**: Maritime — wet winters, warm dry summers. Slow to drought.
**What this plot tests**:
- **Intentionally low N (38 mg/kg)**: this would trigger a "nitrogen low" warning under global thresholds (low=30 is close, but wheat thresholds low=50 would definitely alarm). Pinot Noir thresholds (low=15) correctly identify this as healthy. This is the primary test case for false-alarm suppression via crop-aware thresholds
- `farming_style: regenerative` — this plot should frequently trigger the regenerative alternatives engine (cover crops, mycorrhizal inoculants) even when no alerts fire, because Elena's approach is specifically designed around non-chemical inputs
- Slow moisture drift (maritime `moisture_drift_per_hour: -0.15`) — tests that the system doesn't over-alert on a naturally moist plot

### The combination
Running all three plots simultaneously surfaces the full range: a plot that starts in warning (Fatima), a plot that will drift into alert (Mykola), and a plot that almost never alerts but exercises the recommendations engine differently (Elena). This is more diagnostic value than three similar "healthy" plots would provide.

---

## Lab report simulation

The `lab_report_generator.py` uses `random.gauss(mean, std)` with agronomically validated distributions (sourced from USDA soil survey data) to generate PDF reports. This serves two purposes:

1. **Test fixtures** for the lab-parser service — you can generate 100 reports and run the parser against all of them without needing a real lab.
2. **Edge case generation** — occasionally a generated report will have extreme values (very low N, very high EC) that trigger alert rules. This is intentional.
