# ADR 004 — Vertex AI (Gemini Pro) for AI Recommendations

**Date:** 2026-03-16
**Status:** Accepted

## Context
TerraSensus needs an AI layer to generate crop suitability recommendations, fertiliser supplier suggestions (with eco-scoring), and interpret lab reports.

## Decision
Use Vertex AI (Gemini Pro) as the primary AI model, accessed via the GCP Vertex AI SDK.

## Rationale
- GCP-native: IAM authentication, no separate API key management, integrates with Cloud Run service accounts
- Gemini Pro handles structured reasoning across soil profile inputs well
- Keeps all services within GCP ecosystem (ADR 001)
- Gemini Vision used as fallback in lab-parser for unstructured scanned documents

## Consequences
- Vertex AI pricing applies per token — prompt templates must be concise
- If Gemini recommendation quality proves insufficient for specific agricultural reasoning, Claude API can be added as a secondary option for that service only
- Prompts are versioned in `services/ai-recommendations/prompts/` and treated as first-class code artifacts
