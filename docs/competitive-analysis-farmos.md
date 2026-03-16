# TerraSensus — farmOS Analysis & Lessons

*Reviewed 2026-03-16. farmOS is a mature, GPL-licensed farm management platform backed by Cornell University, active since 2011, with contributions from 150+ farmers and conservation organisations.*

Source: https://github.com/farmOS/farmOS | https://farmos.org

---

## What farmOS Is

A Drupal-based farm record-keeping and management platform. It is not a sensor analytics tool — it is a comprehensive farm operating system. It models everything that happens on a farm: what assets exist, where they are, what events occurred, and what was measured.

**Maturity**: Production-deployed at research institutions, conservation organisations, and commercial farms worldwide.

---

## farmOS Data Model — The Fundamental Pattern

farmOS separates three distinct concepts that most agriculture apps conflate:

```
ASSETS (things)           LOGS (events)              QUANTITIES (measurements)
─────────────────         ──────────────────          ──────────────────────────
Land                      Seeding log                 pH: 6.8 (unit: pH)
Plants/Plantings          Harvest log                 Nitrogen: 85 mg/kg
Animals                   Observation log             Yield: 4.2 t/ha
Equipment                 Lab test log                Rainfall: 22 mm
Structures                Maintenance log
Sensors ◄─────────────── Movement log
Water sources             Inventory log
                          Activity log
                               │
                               └── References one or more Assets
                               └── Contains one or more Quantities
```

**Key insight**: A log is not just a record — it is the historical audit trail. Assets are minimal; Logs build the rich history. This is agronomically correct: what matters on a farm is not just "what exists" but "what happened to it, when."

---

## Critical Domain Knowledge Embedded in farmOS

### 1. Location as Computed State
farmOS does not have a mutable `location` field on assets. Instead, location is **derived from the most recent Movement Log** at any given timestamp. This means:
- You can query "where was this tractor on March 5th?" and get the correct answer
- Moving an asset creates an immutable historical record
- Assets can themselves be locations (a greenhouse, a field plot, a shipping container)

### 2. Fixed vs. Movable Assets
- **Fixed assets** (Land, Buildings, Water sources): have intrinsic geometry; they don't move
- **Movable assets** (Equipment, Animals, Crop plantings in containers): location derived from logs

### 3. Quantities — Flexible Measurement Units
Every measurement in farmOS is a `Quantity` with:
- `value`: decimal (stored as numerator/denominator fraction for precision)
- `unit`: term from a user-managed vocabulary (kg, mg/kg, %, dS/m, t/ha...)
- `label`: optional disambiguator when multiple quantities on the same log

This allows any measurable parameter to be recorded on any log type without schema changes.

### 4. User-Generated Taxonomies
farmOS does not hardcode classifications. It generates vocabulary terms dynamically as users create them. This acknowledges that farming is regionally and culturally diverse — what a UK farmer calls a "ley" a US farmer calls a "pasture". The system adapts.

### 5. Sensor as Asset, Data Stream as Measurement Activity
- **Sensor** = Asset (can move, can be reassigned to different plots)
- **Data Stream** = the continuous measurement record associated with a Sensor Asset and a Land Asset
- Multiple sensors can share or be reassigned to Data Streams
- Threshold alerts are configured per Data Stream, not per sensor hardware

---

## What farmOS Has That TerraSensus Does Not (Yet)

| farmOS Capability | Current TerraSensus State | Action |
|---|---|---|
| **Asset entity hierarchy** (Land, Plants, Equipment, Structures, Sensors) | Single `plot` concept only | Expand data model — see below |
| **Log entity type** (seeding, harvest, observation, lab test, maintenance, movement) | No discrete event logging | Add `activity_logs` table — critical |
| **Quantity type** (flexible value + unit + label per measurement) | Fixed sensor columns only | Add `quantities` table for lab results and manual observations |
| **Crop lifecycle** (planting → growth stages → harvest logs) | Missing entirely | Add `crop_cycles` table |
| **GeoJSON polygon geometry** on plots | lat/lng point only | Add `geometry` field (WKT/GeoJSON) to plots — enables field boundary mapping |
| **Movement logs** (location as computed state) | Static plot coordinates | For mobile assets (equipment, sensors) — important for phase 2 |
| **User-defined taxonomies** / vocabularies | Fixed enums only | Allow farmers to define their own crop types, unit names, activity categories |
| **Multi-asset relationships** | Plot is standalone | Equipment can be logged against a plot; animals can be in a field — m2m relationships |
| **Pest/disease observation logs** | Missing | Add as a log type; Gemini Vision for image-based detection (from competitive analysis) |
| **Maintenance logs** for sensors | Missing | Important for phase 2 when real sensors are buried in fields |
| **Inventory logs** (computed current stock) | Missing | Fertiliser inventory tracking for the cost-benefit analysis |
| **Plan entity** (organise logs/assets around a goal) | Missing | "Spring wheat planting plan" — container for related activities |

---

## What TerraSensus Has That farmOS Does Not

| TerraSensus Capability | farmOS State |
|---|---|
| **Continuous sensor simulation** (time-series with drift, noise, events) | No simulation — requires real hardware |
| **GCP cloud pipeline** (Pub/Sub → Cloud Run → BigQuery) | Self-hosted Drupal only |
| **AI recommendations** (Vertex AI / Gemini Pro) | No AI — data capture only |
| **Cost-benefit / ROI analysis** | No financial analysis |
| **Ecological impact scoring** | No eco-scoring |
| **Regenerative alternatives engine** | No recommendations layer at all |
| **Drought prediction** (Open-Meteo + moisture trend) | No predictive analytics |
| **Lab report PDF parsing** (Document AI + Gemini Vision) | Manual data entry only |
| **ELT analytics pipeline** (dbt + BigQuery) | PostgreSQL only, no analytics layer |
| **CI/CD + IaC** | No deployment automation |
| **Sector expansion** (marine, bioremediation) | Agriculture only |

---

## Recommended Data Model Changes for TerraSensus

Based on farmOS domain knowledge, the TerraSensus PostgreSQL schema should be extended:

### New / Modified Tables

```sql
-- Plots already exist — add geometry field
ALTER TABLE plots ADD COLUMN geometry JSONB;  -- GeoJSON polygon
ALTER TABLE plots ADD COLUMN is_fixed BOOLEAN DEFAULT true;

-- Assets: expand beyond plots to model the full farm
CREATE TABLE assets (
    id UUID PRIMARY KEY,
    farm_id UUID NOT NULL,
    asset_type VARCHAR NOT NULL,  -- land | plants | equipment | structure | sensor | water
    name VARCHAR NOT NULL,
    geometry JSONB,               -- GeoJSON for fixed assets
    is_location BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Activity Logs: discrete farm events (the farmOS "Log" pattern)
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY,
    plot_id UUID REFERENCES plots(id),
    log_type VARCHAR NOT NULL,    -- observation | lab_test | seeding | harvest |
                                  -- fertiliser_application | maintenance | movement | pest
    status VARCHAR DEFAULT 'done', -- done | pending
    notes TEXT,
    logged_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quantities: flexible measurements attached to logs (farmOS Quantity pattern)
CREATE TABLE quantities (
    id UUID PRIMARY KEY,
    log_id UUID REFERENCES activity_logs(id),
    label VARCHAR,                -- e.g. "nitrogen", "yield", "moisture"
    value NUMERIC NOT NULL,
    unit VARCHAR NOT NULL,        -- mg/kg, %, t/ha, dS/m, pH, mm ...
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crop Cycles: planting-to-harvest lifecycle per plot
CREATE TABLE crop_cycles (
    id UUID PRIMARY KEY,
    plot_id UUID REFERENCES plots(id),
    crop_type VARCHAR NOT NULL,
    variety VARCHAR,
    planted_at DATE,
    expected_harvest_at DATE,
    harvested_at DATE,
    yield_t_ha NUMERIC,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Key Design Decisions Adopted from farmOS
1. **Logs are immutable once `status = done`** — they form the audit trail
2. **Quantities are attached to logs, not to plots** — flexible, no schema changes needed for new measurement types
3. **`activity_logs.log_type` covers all event types** — fertiliser applications (for ROI), pest observations, seeding, harvest — one table, one pattern
4. **GeoJSON geometry on plots** — enables Mapbox/Leaflet field boundary visualisation on the web dashboard

---

## Things farmOS Got Right That We Should Follow

1. **Never delete logs** — mark as `status: done` or `status: pending`, never DELETE rows. Farm records are legal and financial documents.
2. **UUID everywhere** — farmOS uses UUIDs as primary keys across all entities. We already do this. Good.
3. **Timestamps on every row** — `created_at`, `updated_at`, `logged_at` (when the event happened, which may differ from when it was recorded). We need `logged_at` separate from `created_at` on logs.
4. **JSON:API or REST with a real spec** — farmOS uses JSON:API. TerraSensus should define an OpenAPI spec for the ingestion service API. Currently undocumented.
5. **Separate `logged_at` from `created_at`** on logs — a farmer may record yesterday's fertiliser application today. `created_at` is when the record was created; `logged_at` is when the event actually happened.

---

## Summary

farmOS took 15 years and 150+ farmers to get its data model right. The core lesson: **a farm is not a collection of sensor readings — it is a collection of assets (things) that have logs (events) containing quantities (measurements)**. TerraSensus should adopt this pattern for manual logs and observations, while preserving its own strength: continuous sensor telemetry, AI analysis, and cloud pipeline that farmOS entirely lacks.

The two biggest immediate changes to make:
1. Add `activity_logs` + `quantities` tables — this gives us the farmOS Log/Quantity pattern for manual events (fertiliser applications, observations, seeding)
2. Add `geometry` field to plots — enables field boundary mapping on the web dashboard
