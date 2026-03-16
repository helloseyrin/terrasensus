# Changelog

All notable changes to TerraSensus are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [Unreleased]

### Added
- Full project skeleton: services, simulator, mobile, web, ELT, infra
- Sensor simulator with Gaussian noise, drift, diurnal temperature cycle, stochastic weather events
- Lab report PDF generator using agronomically validated distributions
- Alert engine with rule-based thresholds for all 7 sensor types
- Drought risk module (Open-Meteo + moisture trend)
- AI recommendations service (Vertex AI / Gemini Pro) with eco-scored supplier prompts
- Lab parser service (Document AI + Gemini Vision fallback)
- dbt ELT pipeline: staging → intermediate → marts (BigQuery)
- React Native (Expo) mobile skeleton: field overview, alerts, recommendations, lab reports
- Shared TypeScript types: SensorReading, LabReport, Alert
- Terraform infrastructure skeleton: Cloud SQL, Pub/Sub, GCS, Cloud Run
- GitHub Actions CI: lint + test for all Python services and TypeScript apps
- GitHub Actions deploy-staging: Cloud Run deployment on merge to main
- 4 Architecture Decision Records (GCP-first, ELT, Expo, Vertex AI)
- Engineering notes: sensor simulation, ELT pipeline, AI recommendations
- CLAUDE.md with full project context for Claude Code sessions
- docker-compose.yml for local development with Pub/Sub emulator
