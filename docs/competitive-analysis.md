# TerraSensus — Competitive Analysis

*Reviewed 2026-03-16 against three open-source precision agriculture projects.*

---

## Projects Reviewed

| Repo | Focus | Primary language | Stars/Status |
|---|---|---|---|
| [Soil-Analyzer](https://github.com/0011Ashwin/Soil-Analyzer) | Soil test interpretation via LLM | Python (Streamlit + Kivy) | MVP/early |
| [AgroTech](https://github.com/Sleide69/Agrotech) | Full farm management platform | Polyglot (TS/Java/Python/PHP/.NET) | Most advanced |
| [PrecisionAgriculture](https://github.com/Lucartis/PrecisionAgriculture) | Sensor monitoring + anomaly detection | C#/.NET | Intermediate |

---

## What They Have That TerraSensus Does Not (Yet)

### From Soil-Analyzer
| Feature | Detail | TerraSensus plan |
|---|---|---|
| **RAG over soil profiles** | 500+ soil profiles as a reference dataset — LLM queries similar profiles to contextualise recommendations | v2: seed a reference dataset from USDA/FAO soil surveys for Gemini to query |
| **Working LLM integration** | Llama 3 70B via Groq API is live and generating real recommendations | Our AI layer is a stub — needs to be wired up |
| **Working Android app** | Kivy/KivyMD app compiles to a real APK | Our Expo app is a skeleton |
| **Radar / gauge chart visualisations** | Plotly radar plots show all nutrients at once — visually effective for soil profiles | Worth adding to our dashboard; good Figma reference |

### From AgroTech
| Feature | Detail | TerraSensus plan |
|---|---|---|
| **Pest detection via image ML** | Upload a photo of a crop → identifies disease/infestation with confidence score | v2 candidate: Gemini Vision can do this; add a `POST /pests/identify` endpoint |
| **Crop lifecycle management** | Full planning-to-harvest event log per crop per plot | Missing from our data model — add a `crop_cycles` table |
| **GraphQL API gateway** | Single query interface across all microservices | Not needed at our current scale; revisit if services multiply |
| **WebSocket real-time updates** | Live sensor feed pushed to browser without polling | Our mobile app uses polling — WebSocket or SSE would be cleaner for web dashboard |
| **Weather API integration** | Meteorological data wired into crop decisions | Partially covered by our drought module (Open-Meteo) but not surfaced in the UI |
| **Multi-format export** | Excel, CSV, PDF, JSON report export | Missing — add to v2 ROI report export |

### From PrecisionAgriculture
| Feature | Detail | TerraSensus plan |
|---|---|---|
| **RabbitMQ message broker** | More portable than GCP Pub/Sub for local dev and multi-cloud | We use Pub/Sub emulator locally — acceptable; RabbitMQ is worth noting for future portability |
| **Anomaly detection engine** | Flags statistically abnormal readings (not just threshold violations) | Our alert engine uses fixed thresholds — statistical anomaly detection (e.g. z-score, IQR) would catch slow degradation that never crosses a hard threshold |
| **pgAdmin UI in docker-compose** | Easy database inspection during dev | Add pgAdmin to our `docker-compose.yml` — low effort, high value |

---

## What TerraSensus Has That None of Them Do

| Capability | Why it matters |
|---|---|
| **CI/CD pipeline** (GitHub Actions) | All three have zero CI/CD. TerraSensus runs lint + tests on every PR, auto-deploys to staging on merge. This is what separates a demo from a product. |
| **Infrastructure as Code** (Terraform) | None use IaC. TerraSensus provisions every GCP resource reproducibly — no manual console clicks, no configuration drift. |
| **ELT analytics pipeline** (Datastream + dbt + BigQuery) | None have a proper analytics layer. TerraSensus separates operational data (Cloud SQL) from analytics (BigQuery), with versioned SQL transforms. |
| **Lab report parsing** (Document AI + Gemini Vision) | No other project handles real lab report uploads. TerraSensus can ingest a PDF from any soil lab and extract structured data — a critical real-world workflow. |
| **Cost-benefit analysis framework** | None calculate money saved. TerraSensus logs every fertiliser application event and computes seasonal ROI — "you could have saved £X." |
| **Ecological impact scoring** | None model the environmental cost of fertiliser choices. TerraSensus surfaces eco-scores, GHG contribution estimates, and biodiversity impact per application. |
| **Regenerative alternatives engine** | None suggest alternatives to synthetic fertilisers. TerraSensus has a dedicated prompt for rice-fish systems, cover crops, biochar, mycorrhizal inoculants, phytoremediation. |
| **Drought prediction module** | None model drought risk. TerraSensus combines Open-Meteo rainfall history with soil moisture trend to produce a risk score. |
| **Sector expansion architecture** | All three are agriculture-only. TerraSensus is explicitly designed to extend to marine conservation, bioremediation, urban ecology, and aquaculture using the same pipeline. |
| **Honest "known unknowns"** | None document what they don't know. TerraSensus explicitly flags unvalidated thresholds and design decisions awaiting expert review — essential for a responsible deployment. |
| **Knowledge management** | None have ADRs, engineering notes, or lessons-learned logs. TerraSensus treats documentation as a first-class deliverable updated continuously during development. |
| **PySensorMQTT upgrade path** | None plan for real hardware. TerraSensus is built to swap the simulator for real MQTT sensors with zero pipeline changes. |
| **Business case documentation** | None articulate why the software should exist. TerraSensus has a full business case with fertiliser cost benchmarks, sector opportunity map, and strategic thesis. |

---

## Feature Gap Summary (Things to Add to TerraSensus Backlog)

Prioritised by impact:

| Priority | Feature | Source | Effort |
|---|---|---|---|
| High | Wire up Vertex AI (Gemini) recommendations — currently a stub | All three have working AI | Medium |
| High | Implement statistical anomaly detection (z-score / IQR) alongside threshold rules | PrecisionAgriculture | Low |
| High | Add `crop_cycles` table to data model (planting → harvest events) | AgroTech | Low |
| Medium | Add pgAdmin to `docker-compose.yml` for local DB inspection | PrecisionAgriculture | Very low |
| Medium | Radar / gauge chart for soil profile overview | Soil-Analyzer | Medium |
| Medium | Pest detection endpoint (`POST /pests/identify` via Gemini Vision) | AgroTech | Medium |
| Medium | Multi-format report export (CSV, PDF, Excel) for ROI reports | AgroTech | Medium |
| Low | WebSocket / SSE push for web dashboard live sensor feed | AgroTech | Medium |
| Low | Seed a reference soil profile dataset (500+ USDA profiles) for RAG | Soil-Analyzer | Low |
| v3 | Crop lifecycle management UI | AgroTech | Large |

---

## Architectural Comparison

```
                    Soil-Analyzer   AgroTech   PrecisionAg   TerraSensus
─────────────────────────────────────────────────────────────────────────
CI/CD               ✗               ✗           ✗             ✓
IaC (Terraform)     ✗               ✗           ✗             ✓
Docker              ✗               ✗           ✓             ✓
Cloud deployment    ✗               ✗           ✗             ✓ (GCP)
Analytics pipeline  ✗               ✗           ✗             ✓ (dbt/BQ)
Real AI integration ✓               ✓           ✗             ✗ (stub)
Mobile app          ✓ (Android)     ✗           ✗             ✓ (Expo, iOS)
Lab report parsing  ✗               ✗           ✗             ✓
Cost-benefit ROI    ✗               ✗           ✗             ✓ (designed)
Eco scoring         ✗               ✗           ✗             ✓ (designed)
Sensor simulation   ✗               ✗           ✓             ✓
Drought prediction  ✗               ✗           ✗             ✓ (designed)
Pest detection      ✗               ✓           ✗             ✗ (v2)
Anomaly detection   ✗               ✗           ✓             ✗ (v2)
Crop lifecycle mgmt ✗               ✓           ✗             ✗ (v2)
Sector expansion    ✗               ✗           ✗             ✓ (designed)
Knowledge mgmt      ✗               ✗           ✗             ✓
```

---

## Summary Verdict

TerraSensus is the only project in this comparison designed to be **deployed, maintained, and extended** rather than demonstrated. The others are prototypes — valuable for ideas, but not production-ready.

The most important gap TerraSensus has right now is that **the AI layer is not yet wired up**. Soil-Analyzer and AgroTech both have working AI recommendations. TerraSensus has better infrastructure to run AI at scale, but the implementation is still `TODO`. That is the highest-priority gap to close.
