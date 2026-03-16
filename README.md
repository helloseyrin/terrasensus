# TerraSensus

> Terra (earth) + Sensus (Latin: sense/perception)

An end-to-end soil health assessment platform for farmers. Combines continuous IoT sensor simulation, lab report parsing, AI-powered recommendations, real-time alerts, and cost-benefit analysis to help farmers optimise crop decisions and reduce fertiliser spend.

---

## Architecture

```
Sensor Simulator (Python)         Lab Report Uploads
  drift + noise + weather events    PDF/image via mobile
        │                                  │
        ▼ GCP Pub/Sub                      ▼ GCS
┌──────────────────────────────────────────────────────┐
│               Backend Services (Cloud Run)           │
│  ┌──────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │Ingestion │  │Alert Engine │  │AI Recommend.   │  │
│  │          │  │rules-based  │  │Vertex AI Gemini│  │
│  │          │  │+ drought    │  │+ eco-scoring   │  │
│  └────┬─────┘  └──────┬──────┘  └───────┬────────┘  │
│       │               │                 │            │
│  ┌────┴──────────────────────────────────────────┐   │
│  │             Lab Parser                        │   │
│  │   Document AI (structured) +                  │   │
│  │   Gemini Vision (scanned/unstructured)        │   │
│  └───────────────────────────────────────────────┘   │
└───────────────────┬──────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
 Cloud SQL (PostgreSQL)    GCP Datastream
 operational data          ──────────────►  BigQuery
        │                                      │
        │ real-time                    dbt transforms
        ▼                                      ▼
    Grafana                            Looker Studio
  (live sensor feeds)             (seasonal reports, ROI)
        │
        ├── React Native (Expo)    ← farmers in the field
        └── Next.js Web            ← farm managers

Push notifications: Firebase Cloud Messaging (critical alerts)
```

---

## Stack

| Layer | Technology |
|---|---|
| Backend services | Python FastAPI (Cloud Run) |
| Mobile | React Native (Expo) — iOS-first |
| Web dashboard | Next.js |
| Message queue | GCP Pub/Sub |
| Operational DB | Cloud SQL (PostgreSQL) |
| Analytics DB | BigQuery (via GCP Datastream) |
| ELT transforms | dbt (staging → intermediate → marts) |
| AI layer | Multi-model fallback chain: Vertex AI (Gemini Pro) → Claude Sonnet → rule-based local |
| Document parsing | Google Cloud Document AI + Gemini Vision |
| File storage | Google Cloud Storage |
| Push notifications | Firebase Cloud Messaging |
| CI/CD | GitHub Actions + Cloud Build |
| Infrastructure | Terraform |
| Live sensor dashboard | Grafana (reads Cloud SQL) |
| Analytics dashboards | Looker Studio (reads BigQuery) |
| Data processing | Polars (not pandas) |

---

## Data Model

Inspired by farmOS (15 years, 150+ farms). Separates three distinct concepts:

```
ASSETS (things)          LOGS (events)                QUANTITIES (measurements)
────────────────         ─────────────────────        ─────────────────────────
Plots / Fields           fertiliser_application  ───► nitrogen_applied: 80 kg/ha
  + GeoJSON geometry     seeding                      cost_per_ha: £45
  + crop_cycles          harvest                 ───► yield: 4.2 t/ha
                         observation             ───► moisture_at_time: 34%
                         lab_test                ───► ph: 6.8, N: 85 mg/kg
                         pest_observation

Sensor Readings (continuous, separate from Logs)
  moisture | temperature | pH | N | P | K | EC — every 30s via Pub/Sub
```

**Key rule**: `logged_at` (when the event happened) is always separate from `created_at` (when it was recorded). A farmer logging Monday's fertiliser application on Wednesday must cross-reference against Monday's soil readings for ROI to be accurate.

---

## Sensors Simulated

| Sensor | Unit | Simulated range | Healthy range | Critical threshold |
|---|---|---|---|---|
| Soil moisture | % | 0–100 | 20–60 | <10 or >80 |
| Soil temperature | °C | -5–45 | 10–25 | <2 or >35 |
| pH | — | 3.5–9.5 | 6.0–7.5 | <5.0 or >8.5 |
| Nitrogen (N) | mg/kg | 0–250 | 30–150 | <15 or >180 |
| Phosphorus (P) | mg/kg | 0–200 | 20–80 | <10 or >120 |
| Potassium (K) | mg/kg | 0–400 | 80–200 | <40 or >250 |
| Electrical conductivity | dS/m | 0–6 | 0.5–2.0 | <0.1 or >3.0 |

Simulation includes: Gaussian noise per reading, hourly drift (e.g. moisture evaporation), diurnal temperature cycle (±5°C sinusoidal), and stochastic weather events (rain spikes, drought multiplier, heatwave).

---

## Lab Report Fields Extracted

| Field | Unit |
|---|---|
| pH | — |
| Nitrogen (N), Phosphorus (P), Potassium (K) | mg/kg |
| Electrical Conductivity | dS/m |
| Organic Matter | % |
| CEC (Cation Exchange Capacity) | meq/100g |
| Calcium (Ca), Magnesium (Mg), Zinc (Zn), Iron (Fe) | mg/kg |
| Sand, Silt, Clay | % |
| Sample depth | cm |
| Plot / Field ID | — |

---

## Getting Started (Local Development)

```bash
git clone https://github.com/helloseyrin/terrasensus.git
cd terrasensus

# Start full local stack (Postgres + all services + Pub/Sub emulator)
docker-compose up

# Services available at:
#   Ingestion:         http://localhost:8001/health
#   Alert Engine:      http://localhost:8002/health
#   AI Recommendations:http://localhost:8003/health
#   Lab Parser:        http://localhost:8004/health
#   pgAdmin (DB UI):   http://localhost:5050
#     login: admin@terrasensus.local / admin

# Run sensor simulator separately (publishes to local Pub/Sub emulator)
cd simulator
pip install -r requirements.txt
python sensor_simulator.py

# Generate synthetic lab report PDFs
python lab_report_generator.py
```

---

## Project Structure

```
terrasensus/
├── .github/
│   ├── ISSUE_TEMPLATE/     # bug, feature, sensor-anomaly, ai-quality
│   └── workflows/          # ci.yml, deploy-staging.yml
├── .claude/                # Claude Code settings + session audit log
├── docs/
│   ├── ADR/                # Architecture Decision Records (001–006)
│   ├── engineering-notes/  # sensor simulation, ELT, AI, data model, cost-benefit, kherson-context
│   ├── specs/              # design documents
│   ├── ai-usage-policy.md  # where AI is and is not acceptable (read before touching AI code)
│   ├── business-case.md    # problem statement, market opportunity, known unknowns
│   ├── competitive-analysis.md  # all four repos + farmer insights + CI/CD learnings
│   ├── backlog.md          # feature backlog (v1 → v3 + icebox)
│   ├── lessons-learned.md  # running log of mistakes and fixes
│   └── figma.md            # design file links and farmer persona
├── services/
│   ├── ingestion/          # FastAPI: Pub/Sub → Cloud SQL
│   ├── alert-engine/       # rule-based thresholds + drought risk + FCM
│   ├── ai-recommendations/ # Vertex AI (Gemini Pro) recommendations
│   └── lab-parser/         # Document AI + Gemini Vision lab report extraction
├── simulator/
│   ├── sensor_simulator.py # continuous time-series with drift/noise/events
│   ├── lab_report_generator.py  # synthetic PDF lab reports (reportlab)
│   ├── weather_events.py   # rain, drought, heatwave event models
│   └── config.yaml         # plot configs, sensor ranges, publish interval
├── elt/
│   └── dbt/                # staging → intermediate → marts (BigQuery)
├── mobile/                 # React Native (Expo) — 4 screens
├── web/                    # Next.js web dashboard
├── infra/                  # Terraform (Cloud SQL, Pub/Sub, GCS, Cloud Run, BigQuery)
├── shared/types/           # TypeScript types shared between mobile and web
│   ├── sensor.ts           # SensorReading, SensorThreshold
│   ├── lab_report.ts       # LabReport, LabResults
│   ├── alert.ts            # Alert, DroughtAlert
│   ├── activity_log.ts     # ActivityLog, Quantity, CropCycle, PlotGeometry
│   ├── cost_benefit.ts     # FertiliserApplication, EcologicalImpact, SeasonROIReport
│   └── onboarding.ts       # PlotRegistration, WatchListItem, OnboardingResponse
├── grafana/dashboards/     # exported Grafana dashboard JSON
├── CLAUDE.md               # Claude Code project memory (read at session start)
├── CHANGELOG.md
└── docker-compose.yml      # full local dev stack
```

---

## Phase Roadmap

| Phase | Data source | Status |
|---|---|---|
| Phase 1 | Python simulator (Gaussian noise + drift + weather events) | Current |
| Phase 2 | PySensorMQTT — real MQTT hardware sensors | Planned |

The simulator's Pub/Sub message schema is identical to what PySensorMQTT will produce. The ingestion service requires no changes when switching to real hardware.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [docs/lessons-learned.md](docs/lessons-learned.md), and [docs/backlog.md](docs/backlog.md).

At end of each Claude Code session, run `/revise-claude-md` to update project memory.
