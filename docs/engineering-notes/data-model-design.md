# Engineering Notes — Data Model Design

Informed by farmOS (farmos.org) — 15 years of real-farm validation across 150+ farms.

---

## The Core Pattern: Assets → Logs → Quantities

The single most important domain insight from farmOS:

> A farm is not a collection of sensor readings. It is a collection of **assets** (things that exist) that have **logs** (events that happened) containing **quantities** (measurements from those events).

```
Plot (Asset)
  └── Activity Log: fertiliser_application, logged_at: 2026-03-10
        └── Quantity: label=nitrogen_applied, value=80, unit=kg/ha
        └── Quantity: label=cost_per_ha, value=45, unit=GBP
  └── Activity Log: lab_test, logged_at: 2026-03-01
        └── Quantity: label=ph, value=6.8, unit=pH
        └── Quantity: label=nitrogen, value=85, unit=mg/kg
        └── Quantity: label=potassium, value=130, unit=mg/kg
  └── Sensor Reading (continuous, every 30s) — separate from Logs
        └── moisture: 34.2%, temperature: 16.1°C, pH: 6.7 ...
```

Logs and sensor readings serve different purposes:
- **Sensor readings**: continuous telemetry, high frequency, machine-generated
- **Activity logs**: discrete events, low frequency, human-initiated, legally significant

Never conflate them in the same table.

---

## logged_at vs created_at

Every log table must have both:
- `created_at`: when the database row was inserted (automatic, server-set)
- `logged_at`: when the event actually happened (set by the user)

A farmer applying fertiliser on Monday but only recording it in the app on Wednesday is normal. Without `logged_at`, you cannot reconstruct the true event timeline. This matters enormously for ROI calculations — you need to know the soil readings at the time of application, not the time of data entry.

---

## Logs are Immutable (Never DELETE)

Farm activity logs are financial and legal records. A fertiliser application log affects the ROI calculation and the ecological score. Never delete them — only allow `status: pending → done` transitions. If a farmer made an error, they add a corrective log entry, not edit or delete the original.

This is the same principle as double-entry bookkeeping: errors are corrected by new entries, not by editing history.

---

## GeoJSON Geometry on Plots

A plot is not just a lat/lng point. It is a field with boundaries — a polygon. Storing GeoJSON geometry enables:
- Area calculation (hectares — needed for cost-per-hectare calculations)
- Map visualisation (Mapbox/Leaflet field boundaries on web dashboard)
- Spatial queries ("which plots overlap with this drainage area?")
- Future: satellite NDVI overlay per field boundary

Store geometry as JSONB in PostgreSQL (native GeoJSON support). For spatial queries, PostGIS extension adds ST_Area, ST_Intersects, etc.

---

## Quantities Table — Why Not Fixed Columns

A common anti-pattern is to add a column for every measurement type:
```sql
-- Anti-pattern
ALTER TABLE sensor_readings ADD COLUMN boron_mg_kg NUMERIC;
ALTER TABLE sensor_readings ADD COLUMN selenium_mg_kg NUMERIC;
```

The `quantities` table pattern is better:
```sql
-- quantities
INSERT INTO quantities (log_id, label, value, unit)
VALUES (log_id, 'boron', 0.3, 'mg/kg');
```

Why: soil lab reports from different labs include different parameters. Some report boron, some don't. Some use mg/kg, some use ppm (same thing). The quantities pattern accommodates any parameter without schema migrations. The trade-off is slightly more complex queries — acceptable for this use case.

---

## User-Generated Taxonomies (Future Consideration)

farmOS allows farmers to define their own crop types, unit names, and activity categories. This is agronomically correct — a UK farmer growing "field beans" calls it something different from a US farmer growing "fava beans" (same crop). Hardcoded enums will frustrate farmers in edge cases.

For TerraSensus v1, enums in `log_type` and unit strings are acceptable. In v2, consider a `vocabularies` table that lets farmers add their own terms.

---

## What farmOS Does Not Have (TerraSensus Strengths)

farmOS is a record-keeping system. It captures what happened but does not:
- Predict what will happen (drought risk, yield forecast)
- Recommend what to do (fertiliser, regenerative alternatives)
- Calculate ROI or ecological cost
- Parse lab reports automatically
- Run continuously without human input (no sensor simulation)
- Deploy on managed cloud infrastructure (self-hosted Drupal only)

TerraSensus is the analytics and intelligence layer that farmOS explicitly leaves to modules and custom code. The data model overlap is intentional — if a farmer already uses farmOS, TerraSensus data should be exportable in a farmOS-compatible format eventually (v3 consideration).
