# TerraSensus — Feature Backlog

Managed here as a running list. Detailed tracking is in GitHub Projects.

## v1 — Skeleton & Foundation
- [ ] GCP infrastructure (Terraform): Cloud SQL, Pub/Sub, GCS, Cloud Run, BigQuery
- [ ] Sensor simulator: continuous time-series with drift, noise, weather events
- [ ] Lab report PDF generator (reportlab)
- [ ] Ingestion service: Pub/Sub → Cloud SQL
- [ ] Alert engine: rule-based thresholds + FCM push notifications
- [ ] Drought risk module: Open-Meteo + moisture trend analysis
- [ ] Lab parser: Document AI + Gemini Vision fallback → structured schema
- [ ] AI recommendations service: Vertex AI (Gemini Pro) — crop, fertiliser, eco-score
- [ ] Mobile app skeleton (Expo): field overview, alerts, recommendations, lab upload
- [ ] Web dashboard skeleton (Next.js): farm overview, per-plot detail
- [ ] ELT pipeline: Datastream (Cloud SQL → BigQuery) + dbt staging models
- [ ] Grafana dashboard: live sensor feeds
- [ ] Looker Studio report: seasonal trends, fertiliser spend
- [ ] CI/CD: GitHub Actions + Cloud Build

## v2 — Analytics & Polish
- [ ] BigQuery ML or Vertex AI for drought prediction model
- [ ] Supplier database integration (local + national eco-certified suppliers)
- [ ] Figma prototype → full mobile UI implementation
- [ ] Historical trend views in mobile app
- [ ] Multi-farm / multi-plot management
- [ ] Offline mode for mobile (poor field connectivity)

## Icebox
- [ ] Google Earth Engine integration for satellite vegetation index (NDVI)
- [ ] Hardware sensor integration (replace simulator)
- [ ] Android support
