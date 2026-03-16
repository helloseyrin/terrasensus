# ADR 005 — Polars over pandas for DataFrame processing

**Date:** 2026-03-16
**Status:** Accepted

## Context
TerraSensus processes continuous time-series sensor data: batch aggregations, trend calculations, anomaly detection windows, and ROI calculations across potentially large historical datasets. A DataFrame library is needed for this work.

## Decision
Use **Polars** instead of pandas wherever tabular data processing is required.

## Rationale
- Polars is built on Apache Arrow and executes in a multi-threaded Rust engine — typically 5–50× faster than pandas for aggregations and filtering on time-series data
- Polars' lazy evaluation API (`pl.scan_*`) allows building query plans that are executed only when needed — maps cleanly to batch ELT processing patterns
- No implicit index — Polars forces explicit column operations, which makes data transformations more readable and less error-prone than pandas' implicit index behaviour
- Strong type system — Polars enforces dtypes strictly, catching type errors at schema definition time rather than silently coercing
- Memory efficiency — Arrow columnar format is significantly more memory-efficient than pandas' row-based storage for the wide sensor reading tables we have

## Consequences
- Team members familiar with pandas will need to learn Polars syntax — migration guide in engineering notes if needed
- Polars' SQL interface (`pl.SQLContext`) can be used for queries that team members prefer to write in SQL
- dbt still uses BigQuery SQL for transforms — Polars is only used in Python service code, not in the ELT layer
