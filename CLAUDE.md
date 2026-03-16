# TerraSensus — Claude Code Project Memory

## Project Overview
TerraSensus is an end-to-end soil health assessment platform for farmers. It combines continuous IoT sensor simulation, lab report uploads/parsing, AI-powered crop and fertiliser recommendations (with ecological sensitivity), drought prediction, and real-time critical alerts.

## Stack
- **Backend**: Python FastAPI, deployed on GCP Cloud Run
- **Mobile**: React Native (Expo) — iOS-first, tested on iPhone
- **Web**: Next.js dashboard
- **Message queue**: GCP Pub/Sub (sensor data pipeline)
- **Operational DB**: Cloud SQL (PostgreSQL)
- **Analytics DB**: BigQuery (ELT via GCP Datastream + dbt)
- **AI layer**: Vertex AI (Gemini Pro) for recommendations
- **Document parsing**: Google Cloud Document AI + Gemini Vision fallback
- **File storage**: Google Cloud Storage (lab report PDFs/images)
- **Push notifications**: Firebase Cloud Messaging
- **CI/CD**: GitHub Actions + Cloud Build
- **Infrastructure**: Terraform
- **Dashboards**: Grafana (real-time, Cloud SQL) + Looker Studio (analytics, BigQuery)

## Repository Structure
- `services/` — FastAPI microservices (ingestion, alert-engine, ai-recommendations, lab-parser); `ai-recommendations/client.py` is the multi-model fallback chain
- `simulator/` — Sensor time-series generator + lab report PDF generator
- `elt/` — dbt project (staging → intermediate → marts) + Datastream config
- `mobile/` — React Native (Expo) app
- `web/` — Next.js web dashboard
- `infra/` — Terraform for all GCP resources
- `shared/types/` — Shared TypeScript types (sensor, lab_report, alert, activity_log, cost_benefit, onboarding)
- `docs/personas.md` — full farmer personas (Mykola/Fatima/Elena): who they are, pain points, what TerraSensus does for them, why these three; Mykola's section includes a toggled developer note on the Kherson occupation and Kakhovka ecocide
- `grafana/` — Exported Grafana dashboard JSON configs

## Data Processing Library Preference
- **Use Polars, not pandas** for all DataFrame/tabular data processing in Python services
- Polars uses Apache Arrow + multi-threaded Rust engine — significantly faster for sensor time-series aggregations
- See ADR 005 for rationale
- Use `polars.LazyFrame` (lazy evaluation) for batch processing; `polars.DataFrame` for small in-memory operations
- Polars SQL context (`pl.SQLContext`) is acceptable for team members who prefer SQL syntax

## Conventions
- Every service has: `Dockerfile`, `tests/` directory, environment config via `.env`
- dbt models follow strict layering: `staging/` → `intermediate/` → `marts/`
- Never mock the database in integration tests — use a real test DB
- Shared TypeScript types live in `shared/types/` — import from there, never redefine
- All Terraform resources are namespaced `terrasensus-*`
- Sensor simulator publishes to Pub/Sub topic `terrasensus-sensor-readings`
- Lab reports upload to GCS bucket `terrasensus-lab-reports`

## AI Usage Policy (CRITICAL — read before touching any AI code)
- See `docs/ai-usage-policy.md` — full policy on where AI is and is not acceptable
- **AI must NEVER be in the path between a sensor reading and a critical alert** — rules.py is synchronous, local, no network
- **AI must NEVER touch financial calculations** — ROI, spend totals, unnecessary application flags are deterministic SQL/Python only
- All AI responses go through the multi-model fallback chain in `services/ai-recommendations/client.py`
- All numeric AI outputs are bounds-checked by `client.py: check_bounds()` before display
- Every AI response displayed to a farmer must show: model source + agronomist disclaimer + flag button
- All threshold values are flagged ⚠ UNVALIDATED until reviewed by a qualified agronomist
- TerraSensus is a decision support tool, not a decision maker

## Data Model Principles (from farmOS analysis)
- **Assets → Logs → Quantities pattern**: plots have activity_logs; logs have quantities (flexible value+unit measurements)
- **logged_at ≠ created_at**: always separate when an event happened from when it was recorded
- **Logs are immutable**: never DELETE logs — they are financial/legal records; errors get a corrective log entry
- **GeoJSON geometry on plots**: store field boundaries as JSONB, not just lat/lng
- **Sensor readings are NOT logs**: continuous telemetry lives in `sensor_readings`; discrete human events live in `activity_logs`
- See `docs/engineering-notes/data-model-design.md` and `docs/competitive-analysis-farmos.md`

## Phase Roadmap
- **Phase 1 (current)**: Simulated sensor data via `simulator/sensor_simulator.py` + Pub/Sub
- **Phase 2**: Replace simulator with **PySensorMQTT** for real MQTT hardware sensor integration. The simulator's output schema intentionally matches what PySensorMQTT would publish — ingestion service requires no changes on switch-over. MQTT topic structure: `terrasensus/farms/{farm_id}/plots/{plot_id}/sensors/{sensor_name}`

## Architecture Decisions
- **ELT over ETL**: Raw data loads into Cloud SQL first, Datastream syncs to BigQuery, dbt transforms — preserves raw data, enables re-transformation
- **Expo over SwiftUI**: Code sharing with Next.js web layer, JS familiarity, React Native new architecture is native-speed for data-display apps
- **Multi-model fallback chain (ADR 006)**: Gemini Pro primary (GCP IAM, native), Claude Sonnet fallback (separate AWS infrastructure — GCP outage won't affect it), rule-based local always available. Correctness failures (wrong values) caught by `client.py: check_bounds()` before display. See `docs/engineering-notes/ai-resilience.md`.
- **Hybrid alert system**: Rule-based engine for instant critical alerts (no latency, no AI), Gemini for deep soil analysis and supplier recommendations
- **Document AI + Gemini Vision**: Document AI for structured lab PDFs, Gemini Vision as fallback for scanned/unstructured reports

## Simulation Personas

Three plots in `simulator/config.yaml` — each represents a real-world edge case:

| Plot ID | Farmer | Region | Crop | Key characteristic |
|---|---|---|---|---|
| plot-ukr-001 | Mykola | Kherson Oblast, Ukraine | Watermelon (GI) | Sandy chernozem, continental climate; K-critical fruiting crop, N ceiling lower than global defaults |
| plot-uzb-001 | Fatima | Ferghana Valley, Uzbekistan | Cotton | Arid, EC already at 2.4 dS/m (warning from day one) |
| plot-ore-001 | Elena | Willamette Valley, Oregon | Pinot Noir | Maritime, low N (38 mg/kg) is intentional — would false-alarm on global defaults |

Crop-aware thresholds in `rules.py` exist specifically because: cotton tolerates higher EC; pinot_noir intentionally runs low N; wheat needs higher N than global defaults.

## Sensor Data Ranges (for simulation)
| Sensor | Unit | Healthy Range | Critical Low | Critical High |
|---|---|---|---|---|
| Moisture | % | 20–60 | <10 | >80 |
| Temperature | °C | 10–25 | <2 | >35 |
| pH | 0–14 | 6.0–7.5 | <5.5 | >8.0 |
| Nitrogen | mg/kg | 30–150 | <20 | >180 |
| Phosphorus | mg/kg | 20–80 | <15 | >120 |
| Potassium | mg/kg | 80–200 | <50 | >250 |
| EC | dS/m | 0.5–2.0 | <0.2 | >3.0 |

Crop-aware overrides in `services/alert-engine/rules.py: CROP_THRESHOLDS` — wheat, cotton, and pinot_noir each have sensor-specific threshold adjustments that take precedence over the global table above. See `get_thresholds(crop)`.

## Lab Report Schema (extracted fields)
pH, N (mg/kg), P (mg/kg), K (mg/kg), EC (dS/m), Organic Matter (%), CEC (meq/100g), Ca (mg/kg), Mg (mg/kg), Zn (mg/kg), Fe (mg/kg), sand (%), silt (%), clay (%), sample_depth_cm, plot_id

## Known Issues
<!-- Claude: update this section when bugs are found during development -->

## Recent Decisions
<!-- Claude: update this section when architectural decisions are made -->

## Session Log
<!-- Claude: append brief notes at end of each session using /revise-claude-md -->
