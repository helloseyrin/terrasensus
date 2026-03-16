# ADR 001 — GCP-First Stack

**Date:** 2026-03-16
**Status:** Accepted

## Context
TerraSensus needs a cloud platform for hosting backend services, storing sensor data, running ML/AI, and managing file uploads (lab reports). Two realistic options: AWS or GCP.

## Decision
Use GCP as the primary cloud platform across all services.

## Rationale
- Native integration between Cloud Run, Pub/Sub, Cloud SQL, BigQuery, Datastream, Document AI, and Vertex AI — avoids cross-cloud glue code
- BigQuery + Looker Studio is a natural ELT analytics stack without additional tooling
- Vertex AI (Gemini Pro) provides the AI recommendation layer without an external API dependency
- Document AI purpose-built for structured document extraction (lab reports)
- Firebase (GCP-owned) handles push notifications seamlessly

## Consequences
- Vendor lock-in to GCP — acceptable given scope and team size
- GCP free tier and startup credits reduce initial cost
- Terraform manages all resources for portability if needed later
