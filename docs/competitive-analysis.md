# TerraSensus — Competitive Analysis & Landscape

*Last updated 2026-03-16. Synthesises findings from four open-source agriculture projects and domain research conducted without direct farmer access.*

---

## Projects Reviewed

| Repo | Focus | Stack | Maturity |
|---|---|---|---|
| [Soil-Analyzer](https://github.com/0011Ashwin/Soil-Analyzer) | Soil test interpretation via LLM | Python, Streamlit, Kivy | MVP |
| [AgroTech](https://github.com/Sleide69/Agrotech) | Full farm management platform | Polyglot (TS/Java/Python/PHP/.NET) | Advanced |
| [PrecisionAgriculture](https://github.com/Lucartis/PrecisionAgriculture) | Sensor monitoring + anomaly detection | C#/.NET, RabbitMQ | Intermediate |
| [farmOS](https://github.com/farmOS/farmOS) | Farm record-keeping + asset management | Drupal/PHP, PostgreSQL | **Production — 15 years, 150+ farms** |

---

## What Each Project Taught Us

### Soil-Analyzer — LLM integration and visualisation

| Insight | TerraSensus response |
|---|---|
| **RAG over soil profiles** — 500+ USDA soil profiles let the LLM contextualise "is 85 mg/kg N good or bad for this region and crop?" | v2: seed a USDA/FAO reference dataset for Gemini to query against |
| **Llama 3 via Groq is live** — working recommendations today, while our AI layer is a stub | Highest-priority gap to close |
| **Radar charts** — plotting all 7 nutrients on one polygon gives farmers an instant visual of soil balance | Add to web dashboard and mobile recommendations screen |
| **Offline-first mobile** — rural farmers have poor connectivity; Kivy app caches data locally | Add to v2 mobile backlog; offline mode for poor field connectivity |

### AgroTech — Domain completeness and real-time architecture

| Insight | TerraSensus response |
|---|---|
| **Pest detection via image upload** — farmer photographs a diseased crop, gets confidence-scored diagnosis | v2: `POST /pests/identify` via Gemini Vision |
| **Crop lifecycle management** — seeding → growth stages → harvest is a first-class entity, not an afterthought | Added `crop_cycles` table to data model and `CropCycle` TypeScript type |
| **WebSocket real-time updates** — browser receives live sensor data pushed from server without polling | Web dashboard v2; mobile currently polls, acceptable for phase 1 |
| **Multi-format export** — farmers need Excel/CSV/PDF, not just JSON | v2 ROI report export |
| **Weather wired into crop decisions** — not just drought risk, but planting windows, frost alerts, harvest windows | Drought module covers part of this; expand to full agro-meteorological events |

### PrecisionAgriculture — Message-driven architecture and anomaly detection

| Insight | TerraSensus response |
|---|---|
| **Statistical anomaly detection** (z-score / IQR) catches slow degradation that never crosses a hard threshold — a plot where moisture slowly trends downward over 14 days, never hitting critical, is a real problem | v2 alert engine: layer statistical detection on top of threshold rules |
| **RabbitMQ** is more portable than GCP Pub/Sub for multi-cloud or on-premise deployments | Acceptable to keep Pub/Sub; note RabbitMQ if portability is needed |
| **pgAdmin in docker-compose** — developers need to inspect the database without writing SQL scripts | ✓ Added to `docker-compose.yml` on port 5050 |

### farmOS — 15 years of real-farm domain knowledge

This is the most important reference project. farmOS was built *with* farmers, not *for* them — the data model reflects what farmers actually do, not what engineers assume they do. Full analysis in `docs/competitive-analysis-farmos.md`.

**The core lesson — Assets → Logs → Quantities:**

> A farm is not a collection of sensor readings. It is a collection of *assets* (things that exist) that have *logs* (events that happened) containing *quantities* (measurements from those events).

| farmOS insight | TerraSensus response |
|---|---|
| **Logs are the audit trail** — every farm event (fertiliser applied, seeding, observation, harvest) is an immutable log entry; never edited or deleted | Added `activity_logs` table and `ActivityLog` TypeScript type; immutability rule in CLAUDE.md |
| **logged_at ≠ created_at** — farmers record Monday's fertiliser on Wednesday; ROI calculation must use Monday's soil readings, not Wednesday's | `logged_at` field on all log tables; documented with concrete failure scenario in engineering notes |
| **Quantities are flexible** — measurement type and unit are not hardcoded columns; any parameter can be added without schema migration | Added `quantities` table pattern to data model |
| **GeoJSON field geometry** — a "plot" is a polygon, not a lat/lng point; needed for area calculation and field boundary mapping | Added `PlotGeometry` TypeScript type; `geometry JSONB` field planned for plots table |
| **Crop cycles are fundamental** — planting → growth stages → harvest is a core workflow, not an edge case | Added `crop_cycles` table |
| **Sensors are assets** — a sensor can move between plots, be replaced, be maintained; it has a lifecycle independent of the data it produces | Data model implication for phase 2 sensor management |
| **User-defined taxonomies** — farmers classify things differently by region and culture; hardcoded enums cause friction | v2 consideration: `vocabularies` table for user-defined terms |

---

## CI/CD Architecture — What We Learned

**The single most consistent gap across all four repos: none have CI/CD.**

Soil-Analyzer, AgroTech, PrecisionAgriculture, and farmOS all require manual builds and manual deployment. This is common in open-source agriculture projects — they are maintained by domain experts (farmers, researchers) who are not DevOps engineers. The result: deployments are manual, inconsistent, and prone to "works on my machine" failures.

### What TerraSensus CI/CD Does

```
Pull Request opened
    │
    ├── lint-test-ingestion      (ruff + pytest)
    ├── lint-test-alert-engine   (ruff + pytest, including rules.py threshold tests)
    ├── lint-test-ai-recommendations (ruff + pytest)
    ├── lint-test-lab-parser     (ruff + pytest)
    ├── lint-test-mobile         (tsc + eslint + jest)
    ├── lint-test-web            (tsc + eslint + jest)
    ├── lint-simulator           (ruff)
    └── dbt-parse                (dbt parse — catches broken SQL models)

Merge to main
    └── deploy-staging           (Cloud Build → Cloud Run, per service)

Manual trigger (production)
    └── deploy-prod              (same pipeline, production environment)
```

### Why This Architecture

**Per-service jobs, not a matrix**: each service has its own named CI job rather than a matrix strategy. This means:
- A mobile TypeScript failure doesn't block an ingestion Python fix from merging
- Failure messages in GitHub are immediately attributed to the right service
- Jobs run in parallel — total CI time is the slowest single service, not the sum of all

**dbt parse in CI**: farmOS has no analytics pipeline; none of the other repos do either. Running `dbt parse` on every PR catches broken SQL models before they reach staging. A broken mart model would silently produce wrong Looker Studio reports — the kind of bug that takes days to trace.

**Threshold rules in CI (`test_rules.py`)**: the alert engine's threshold values are agronomically significant. A wrong critical threshold could fail to alert a farmer about dangerously low moisture, or spam them with false positives. Having threshold tests in CI means any change to `rules.py` must pass a test that validates the boundary behaviour.

### What CI/CD Cannot Replace (Farmer Validation)

CI/CD validates that the code works correctly. It cannot validate that the thresholds, recommendations, and ROI calculations are *agronomically correct*. For that, domain expert review is required — see the "Known Unknowns" section in `docs/business-case.md`.

---

## Farmer Insights — Without Knowing Any Farmers

*Synthesised from farmOS documentation, peer-reviewed agronomy literature, FAO datasets, USDA soil surveys, and analysis of the above repos. All of this requires validation by real farmers before being treated as authoritative.*

### How Farmers Actually Work (Inferred)

**Record-keeping is retrospective, not real-time.**
farmOS's `logged_at` vs `created_at` distinction exists because farmers do not open an app every time they apply fertiliser. They do it at end of day, end of week, sometimes from memory. Any app that requires immediate data entry will fail. The UX must make retrospective entry as easy as real-time entry.

**Fertiliser application is based on habit, not data.**
No other project in this comparison had a farmer complaining that they had too much soil data. The problem is the opposite: most farmers have never seen a soil sensor reading in their lives. They apply based on last year's rates, their agronomist's blanket recommendation, or what their neighbour does. This means:
- The app must not assume the farmer knows what mg/kg means
- All readings should be translated to plain English: "Your nitrogen is low — about half what wheat needs at this stage"
- The first value TerraSensus delivers is *surprise*: "You have never seen this before"

**Connectivity is unreliable in fields.**
Soil is in fields. Fields are often rural. Rural often means poor mobile signal. AgroTech's offline-first approach and Soil-Analyzer's cached Android app both address this. TerraSensus mobile must:
- Cache the last known readings locally
- Queue alert acknowledgements and log entries for sync when connected
- Never show a blank screen or spinner — show stale data with a "last updated X ago" label instead

**Farmers are economically rational, not environmentally idealistic.**
The regenerative agriculture framing must be grounded in cost savings first, ecological benefit second. A farmer won't switch from urea to compost because it's better for the soil microbiome. They will switch if you can show: "compost costs £Y/ha less and achieves the same yield outcome over a 3-year window." Eco-scoring in TerraSensus is informational, not moralistic.

**Soil lab reports are expensive and infrequent.**
A professional soil analysis costs £50–300 per sample. Most farmers test once or twice a year, if at all. This is why continuous sensors are transformative — but also why the app must treat lab report results as high-value, high-trust data points and sensor readings as high-frequency, lower-trust proxies. The two must be displayed and weighted differently.

**Field boundaries are important for compliance, not just mapping.**
In the EU (CAP), UK (SFI/ELMs), and US (USDA FSA), farmers are required to submit field boundary maps and activity records to claim subsidies. A field without a GeoJSON polygon is harder to use for subsidy claims. This is an underappreciated driver for adoption — if TerraSensus can produce subsidy-compatible field records, it solves a real administrative burden.

**Multiple plots, different crops, different problems — simultaneously.**
No farmer has one field. A 50ha farm might have 8 plots in different states of a 4-year rotation. The app must handle the "I'm looking at the wrong field" problem — the home screen must immediately orient the farmer to the right plot, ideally with GPS context.

### What We Still Don't Know (Requires Real Farmers)

| Unknown | Why it matters |
|---|---|
| Are our sensor threshold values correct for UK/EU crops? | `rules.py` values are from literature — may not match real farm expectations |
| How often do farmers actually apply fertiliser per season? | Determines how valuable the "unnecessary application" ROI flag is |
| Do farmers trust AI recommendations or ignore them? | If they don't trust it, eco-scoring and supplier suggestions are noise |
| What does a soil lab report actually look like from a real UK lab? | Our PDF generator is modelled on general format — may not match real lab output |
| What's the real cost of an application event? | Our £45/ha estimate is approximate — varies wildly by product, region, crop |
| Would a farmer pay for this app? If so, how much? | Critical for viability; no project reviewed addressed monetisation |

---

## Full Feature Comparison

```
                      Soil-   Agro-  Precision  farmOS   Terra-
                      Analyzer Tech   Ag                  Sensus
───────────────────────────────────────────────────────────────
CI/CD pipeline          ✗       ✗       ✗         ✗        ✓
IaC (Terraform)         ✗       ✗       ✗         ✗        ✓
Cloud deployment        ✗       ✗       ✗         ✗        ✓ GCP
ELT analytics (dbt/BQ)  ✗       ✗       ✗         ✗        ✓
Working AI integration  ✓       ✓       ✗         ✗        ✗ stub
Mobile app              ✓ Android ✗     ✗         ✗        ✓ Expo/iOS
Lab report parsing      ✗       ✗       ✗         manual   ✓
Cost-benefit ROI        ✗       ✗       ✗         ✗        ✓ designed
Ecological scoring      ✗       ✗       ✗         ✗        ✓ designed
Sensor simulation       ✗       ✗       ✓         ✗        ✓
Drought prediction      ✗       ✗       ✗         ✗        ✓ designed
Statistical anomaly det.✗       ✗       ✓         ✗        ✗ v2
Pest detection          ✗       ✓       ✗         ✗        ✗ v2
Crop lifecycle          ✗       ✓       ✗         ✓        ✓ designed
Activity logs (Log pat.)✗       partial ✗         ✓        ✓ designed
Flexible quantities     ✗       ✗       ✗         ✓        ✓ designed
Field geometry (GeoJSON)✗       ✗       ✗         ✓        ✓ designed
Subsidy-compatible recs ✗       ✗       ✗         ✓        ✗ v3
Sector expansion        ✗       ✗       ✗         ✗        ✓ designed
Knowledge management    ✗       ✗       ✗         ✓ docs   ✓
Domain expert review    ✗       ✗       ✗         ✓ comm.  ✗ needed
```

---

## Priority Gap List (Updated)

| Priority | Gap | Where it came from | Effort |
|---|---|---|---|
| **Critical** | Wire up Vertex AI recommendations — AI layer is a stub | All three apps have working AI | Medium |
| **Critical** | Implement `activity_logs` + `quantities` tables in DB schema | farmOS data model | Low |
| **Critical** | Add `logged_at` to all log tables with ROI calculation logic | farmOS + engineering notes | Low |
| High | Statistical anomaly detection (z-score / IQR) in alert engine | PrecisionAgriculture | Low |
| High | `geometry` GeoJSON field on plots | farmOS | Low |
| High | Offline mode + stale-data UX for mobile (no blank screens in fields) | Soil-Analyzer + farmer insight | Medium |
| High | Radar/gauge chart for soil overview screen | Soil-Analyzer | Medium |
| Medium | Seed USDA/FAO reference soil profile dataset for RAG | Soil-Analyzer | Low |
| Medium | Pest detection endpoint via Gemini Vision | AgroTech | Medium |
| Medium | Multi-format export (CSV, PDF, Excel) for ROI reports | AgroTech | Medium |
| Medium | GPS-aware plot selection on mobile home screen | Farmer insight | Medium |
| Medium | Plain-English translation of all sensor readings (no mg/kg on screen) | Farmer insight | Medium |
| Low | WebSocket / SSE for web dashboard live feed | AgroTech | Medium |
| Low | CAP/SFI subsidy-compatible field record export | farmOS + farmer insight | Large |
| v3 | User-defined taxonomies (vocabularies table) | farmOS | Medium |
| v3 | farmOS data export compatibility | farmOS | Large |

---

## Summary

**What this landscape confirms:**

All four projects are missing the same things: automated deployment, cloud infrastructure, and an analytics pipeline. TerraSensus is the only project in this comparison built to be deployed and maintained at scale, not just demonstrated.

**The most important things learned from each:**
- **Soil-Analyzer**: RAG over soil profiles makes LLM recommendations dramatically better; build this before going live with Gemini
- **AgroTech**: crop lifecycle and pest detection are real farmer workflows, not edge cases
- **PrecisionAgriculture**: statistical anomaly detection catches slow degradation that threshold rules miss entirely
- **farmOS**: the data model is the product; 15 years of real-farm feedback produced the Assets → Logs → Quantities pattern — adopt it

**The single most important gap right now**: the AI layer is a stub. Every other project reviewed has working recommendations. TerraSensus has better infrastructure to *run* AI, but nothing to *show* yet. That changes in v1 implementation.
