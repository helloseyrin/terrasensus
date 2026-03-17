# TerraSensus — MVP0 Checklist: Before Going Live on GCP

*MVP0 = minimum required to deploy a working, real-data version to GCP and have it not embarrass you. Not feature-complete — just honest and functional.*

---

## 🏗️ Infrastructure (Terraform)

- [ ] GCP project created and billing enabled
- [ ] `terraform apply` runs cleanly — Cloud SQL, Pub/Sub, Cloud Run, BigQuery, GCS all provisioned
- [ ] Secrets (DB credentials, API keys) stored in GCP Secret Manager, not hardcoded
- [ ] VPC and private networking configured (Cloud SQL not publicly exposed)
- [ ] Service accounts with least-privilege IAM roles for each Cloud Run service

---

## 🗄️ Database

- [ ] Cloud SQL PostgreSQL instance live (not just local Docker)
- [ ] All migrations run cleanly on the live instance
- [ ] `activity_logs` + `quantities` tables added (farmOS Log/Quantity pattern)
- [ ] `crop_cycles` table added (planting → harvest lifecycle per plot)
- [ ] `logged_at` field on all log tables (separate from `created_at` — required for correct ROI)
- [ ] `geometry` GeoJSON field on plots
- [ ] At least one real plot seeded (Mykola / Fatima / Elena persona data, or your own test plot)

---

## ⚙️ Backend Services (Cloud Run)

### Ingestion service
- [ ] Subscribes to Pub/Sub and writes sensor readings to Cloud SQL
- [ ] Handles malformed messages without crashing
- [ ] Health check endpoint returns 200

### Alert engine
- [ ] Rule-based thresholds fire correctly for all 7 sensors
- [ ] Drought risk module runs (Open-Meteo integration live, not mocked)
- [ ] FCM push notification reaches a real device (even a test one)
- [ ] **No AI in this service** — rule-based only, confirmed

### AI recommendations
- [ ] Vertex AI (Gemini Pro) call works with a real GCP project + IAM credentials
- [ ] Claude Sonnet fallback triggers when Gemini fails
- [ ] Rule-based local fallback triggers when both AI calls fail
- [ ] `check_bounds()` bounds checker catches agronomically impossible values
- [ ] Every response includes model name + agronomist disclaimer

### Lab parser
- [ ] Document AI call works with a real scanned PDF
- [ ] Gemini Vision fallback works for unstructured/handwritten reports
- [ ] Extracted fields written correctly to Cloud SQL schema

---

## 📡 Sensor Pipeline

- [ ] Simulator publishes to **real GCP Pub/Sub** (not local emulator)
- [ ] Ingestion service picks up messages end-to-end
- [ ] At least one weather event (rain spike / drought) flows through and triggers an alert

---

## 📊 Analytics

- [ ] GCP Datastream replicating Cloud SQL → BigQuery (no manual export)
- [ ] dbt staging models run cleanly on BigQuery
- [ ] At least one mart table queryable (e.g. sensor readings by plot)

---

## 📱 Mobile App

- [ ] Expo build runs on a real iOS device (not just simulator)
- [ ] Connects to Cloud Run services (not localhost)
- [ ] Field overview screen loads real plot data
- [ ] Alert screen receives a real FCM push notification
- [ ] Lab report upload sends a real PDF to the lab parser

---

## 🔐 Security minimum bar

- [ ] No API keys or secrets in source code or `.env` files committed to repo
- [ ] All Cloud Run services require authentication (not publicly open)
- [ ] HTTPS only — no plain HTTP endpoints exposed

---

## 🚦 CI/CD

- [ ] `ci.yml` passes on push to main (tests, lint)
- [ ] `deploy-staging.yml` deploys successfully to a staging environment
- [ ] At least one service has a passing test suite (alert-engine rules are the most critical)

---

## ✅ Smoke test before calling it live

- [ ] Start simulator → sensor readings appear in Cloud SQL
- [ ] A critical threshold breach triggers an FCM notification on a real device
- [ ] Upload a lab report PDF → structured data appears in Cloud SQL
- [ ] AI recommendation returns a real Vertex AI response with crop-aware advice
- [ ] BigQuery mart table has data after Datastream sync
- [ ] Mobile app loads the above data end-to-end without errors

---

## What is explicitly NOT in MVP0

- ROI / cost-benefit analysis (v2)
- Ecological impact scoring (v2)
- Regenerative alternatives engine (v2)
- Web dashboard (v2)
- Looker Studio / Grafana (v2)
- Real hardware sensors / PySensorMQTT (icebox)
- Multi-farm management (v2)

---

*When all boxes above are ticked, run `terraform apply` on production, point the simulator at it, and TerraSensus is live.*
