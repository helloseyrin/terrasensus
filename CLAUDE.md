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
- `services/` — FastAPI microservices (ingestion, alert-engine, ai-recommendations, lab-parser)
- `simulator/` — Sensor time-series generator + lab report PDF generator
- `elt/` — dbt project (staging → intermediate → marts) + Datastream config
- `mobile/` — React Native (Expo) app
- `web/` — Next.js web dashboard
- `infra/` — Terraform for all GCP resources
- `shared/types/` — Shared TypeScript types (sensor, lab_report, alert)
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
- **Gemini over Claude for AI layer**: GCP-native, avoids external API dependency, Vertex AI IAM integrates cleanly with rest of GCP stack
- **Hybrid alert system**: Rule-based engine for instant critical alerts (no latency), Gemini for deep soil analysis and supplier recommendations
- **Document AI + Gemini Vision**: Document AI for structured lab PDFs, Gemini Vision as fallback for scanned/unstructured reports

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

## Lab Report Schema (extracted fields)
pH, N (mg/kg), P (mg/kg), K (mg/kg), EC (dS/m), Organic Matter (%), CEC (meq/100g), Ca (mg/kg), Mg (mg/kg), Zn (mg/kg), Fe (mg/kg), sand (%), silt (%), clay (%), sample_depth_cm, plot_id

## Known Issues
<!-- Claude: update this section when bugs are found during development -->

## Recent Decisions
<!-- Claude: update this section when architectural decisions are made -->

## Session Log
<!-- Claude: append brief notes at end of each session using /revise-claude-md -->
