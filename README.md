# TerraSensus

> Terra (earth) + Sensus (Latin: sense/perception)

An end-to-end soil health assessment platform for farmers. Combines continuous IoT sensor simulation, lab report analysis, AI-powered recommendations, and real-time alerts to help farmers optimise crop decisions and reduce fertiliser costs.

## Architecture

```
Sensor Simulator (Python)       Lab Report Uploads
        │                              │
        ▼ GCP Pub/Sub                  ▼ GCS
┌───────────────────────────────────────────────────┐
│              Backend Services (Cloud Run)         │
│  Ingestion │ Alert Engine │ AI Recommendations    │
│            │              │ Lab Parser            │
└────────────┼──────────────┼──────────────────────┘
             ▼              ▼
     Cloud SQL (PostgreSQL)    BigQuery (analytics)
             │                       │
    ─────────┴───────────────────────┴─────
    │                 │                   │
React Native      Next.js Web         Grafana +
(Mobile App)      (Dashboard)         Looker Studio
```

## Stack

| Layer | Technology |
|---|---|
| Backend services | Python FastAPI (Cloud Run) |
| Mobile | React Native (Expo) |
| Web dashboard | Next.js |
| Message queue | GCP Pub/Sub |
| Operational DB | Cloud SQL (PostgreSQL) |
| Analytics DB | BigQuery |
| ELT transforms | dbt |
| AI layer | Vertex AI (Gemini Pro) |
| Document parsing | Google Cloud Document AI + Gemini Vision |
| File storage | Google Cloud Storage |
| Push notifications | Firebase Cloud Messaging |
| CI/CD | GitHub Actions + Cloud Build |
| Infrastructure | Terraform |
| Analytics dashboards | Grafana + Looker Studio |

## Getting Started

```bash
# Clone the repo
git clone https://github.com/helloseyrin/terrasensus.git
cd terrasensus

# Start local dev environment
docker-compose up

# Run sensor simulator
cd simulator && python sensor_simulator.py
```

## Project Structure

```
terrasensus/
├── .github/            # CI/CD workflows, issue templates
├── .claude/            # Claude Code settings + session logs
├── docs/               # ADRs, specs, lessons learned, Figma links
├── services/           # Backend microservices (FastAPI)
├── simulator/          # Sensor + lab report data simulators
├── elt/                # dbt models + GCP Datastream config
├── mobile/             # React Native (Expo) app
├── web/                # Next.js web dashboard
├── infra/              # Terraform (GCP resources)
├── shared/             # Shared TypeScript types
└── grafana/            # Grafana dashboard configs
```

## Sensors Simulated

| Sensor | Unit | Range |
|---|---|---|
| Soil moisture | % | 0–100 |
| Soil temperature | °C | 0–40 |
| pH | 0–14 | 4.5–8.5 |
| Nitrogen (N) | mg/kg | 0–200 |
| Phosphorus (P) | mg/kg | 0–150 |
| Potassium (K) | mg/kg | 0–300 |
| Electrical conductivity | dS/m | 0–4 |

## Lab Report Fields Extracted

pH, N, P, K, EC, Organic Matter %, CEC, Ca, Mg, Zn, Fe, soil texture, sample depth, plot ID

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/lessons-learned.md](docs/lessons-learned.md).
