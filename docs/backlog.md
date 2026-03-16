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

## v2 — Cost-Benefit Analysis & Regenerative Intelligence
- [ ] Fertiliser application event logging (type, quantity, cost, date, plot)
- [ ] ROI report: unnecessary applications flagged vs soil readings at time of application
- [ ] Season savings calculator: "you could have saved £X if you followed recommendations"
- [ ] Ecological impact scoring per fertiliser type (biodiversity, GHG, runoff risk)
- [ ] Regenerative alternatives recommendation engine (rice-fish systems, cover crops, biochar, mycorrhizal inoculants, phytoremediation)
- [ ] Looker Studio ROI dashboard: spend vs soil health trend, eco-score over time
- [ ] Domain expert review mode: flag threshold values + recommendations for agronomist sign-off
- [ ] BigQuery ML or Vertex AI for drought prediction model
- [ ] Supplier database integration (local + national eco-certified suppliers)
- [ ] Figma prototype → full mobile UI implementation
- [ ] Historical trend views in mobile app
- [ ] Multi-farm / multi-plot management
- [ ] Offline mode for mobile (poor field connectivity)

## v3 — Sector Expansion
- [ ] Marine / coastal water quality monitoring (same pipeline, different sensor schema)
- [ ] Bioremediation tracking (phytoremediation progress: heavy metals, hydrocarbons)
- [ ] Urban ecology / green infrastructure module
- [ ] Soil carbon sequestration measurement for carbon credit market reporting
- [ ] Aquaculture pond/tank water quality module

## Icebox
- [ ] Google Earth Engine: satellite NDVI vegetation stress index per plot
- [ ] Phase 2: PySensorMQTT — real MQTT hardware sensor integration (replaces simulator)
- [ ] LoRaWAN / NB-IoT connectivity for poor rural signal coverage
- [ ] Android support
- [ ] Earthworm density estimator (biodiversity proxy from organic matter + pH + pesticide history)
- [ ] Farmer community: anonymised regional soil health benchmarking ("your N is 30% below farms of similar size in your county")
