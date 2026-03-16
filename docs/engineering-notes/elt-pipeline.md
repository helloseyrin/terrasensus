# Engineering Notes — ELT Pipeline

---

## Why ELT, not ETL

Traditional ETL transforms data *before* loading it into the warehouse. Modern cloud stacks prefer ELT: load raw data first, transform it in-place using SQL.

**Concrete benefit for TerraSensus**: if we discover a bug in how we calculate the daily moisture average, we can fix the dbt model and re-run the transform against the already-loaded raw data. With ETL, a bug in the transform means the raw data may be gone — you'd need to re-ingest from source.

## dbt model layering

```
staging/        Raw → cleaned, typed, renamed. Materialised as views (no storage cost).
intermediate/   Joins and enrichment. Also views.
marts/          Final analytical tables for Looker Studio and Grafana. Materialised as tables (pre-aggregated, fast to query).
```

This layering means Looker Studio always queries a pre-aggregated `mart_*` table, not raw sensor data. A dashboard query over 30 days of readings for 3 plots costs the same whether you have 1,000 or 10,000,000 rows in the raw table.

## Grafana vs Looker Studio split

- **Grafana** → reads Cloud SQL directly. Used for real-time sensor monitoring (last 1h, last 24h). Sub-second latency. Farmers and field operators.
- **Looker Studio** → reads BigQuery `mart_*` tables. Used for weekly/monthly management reports, fertiliser spend analysis, seasonal trends. Farm managers and agronomists.

The split avoids putting real-time operational queries on BigQuery (unnecessary cost) and avoids using Grafana for long-horizon analytics (it's not designed for that).

## Datastream replication lag

GCP Datastream replicates Cloud SQL changes to BigQuery with a lag of approximately 1–2 minutes. This is fine for Looker Studio (analytics), but means Grafana must never query BigQuery for real-time data — always Cloud SQL directly.
