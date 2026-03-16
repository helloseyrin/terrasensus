# ADR 002 — ELT over ETL for Analytics Pipeline

**Date:** 2026-03-16
**Status:** Accepted

## Context
Sensor readings and lab report data need to flow from the operational database (Cloud SQL) into an analytics store for Looker Studio and Grafana dashboards.

## Decision
Use ELT (Extract → Load → Transform) via GCP Datastream + dbt, not ETL.

## Rationale
- Raw data is preserved in BigQuery — can re-run transforms without re-ingesting
- dbt provides version-controlled, tested SQL transforms with clear staging → intermediate → marts layering
- GCP Datastream handles CDC (change data capture) from Cloud SQL to BigQuery with zero custom code
- Modern standard for cloud-native data pipelines

## Consequences
- BigQuery costs apply for storage and query compute — acceptable at this scale
- dbt adds a learning curve; pay-off is maintainable, documented transform logic
- Grafana reads Cloud SQL directly for real-time feeds (sub-second), Looker Studio reads BigQuery marts for historical analysis
