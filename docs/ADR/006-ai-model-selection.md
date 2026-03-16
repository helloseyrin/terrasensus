# ADR 006 — AI Model Selection: Gemini vs Claude vs Others

**Date:** 2026-03-16
**Status:** Decided — Gemini Pro on Vertex AI, with Claude API as documented fallback

---

## The Question

Is Vertex AI (Gemini Pro) the right model for TerraSensus recommendations, or should we use Claude (Anthropic) or another provider?

## Data Centre Consideration

The question was raised: does Google having the most data centres globally make Gemini the right choice?

**Short answer**: data centre count is not the right metric here. What matters is:
- **Latency to your Cloud Run region** (europe-west2 for us) — both Vertex AI and Claude API have endpoints in Europe
- **Accuracy on structured agricultural reasoning tasks** — model quality, not geography
- **Integration cost** — Vertex AI uses GCP IAM (no separate API key); Claude needs an Anthropic API key and adds an external dependency
- **Cost per token** — Gemini 1.5 Pro and Claude Sonnet are comparable; Gemini Flash is significantly cheaper for high-frequency calls

## Honest Model Comparison for This Use Case

| Dimension | Gemini 1.5 Pro (Vertex AI) | Claude Sonnet (Anthropic API) |
|---|---|---|
| Structured JSON output | ✓ native `application/json` response mime | ✓ via tool use or prompt |
| Agricultural domain knowledge | Good — trained on broad web corpus | Good — similar training |
| Long context (full soil profile + history) | ✓ 1M token context | ✓ 200K token context |
| GCP IAM integration | ✓ native — no separate API key | ✗ external API key required |
| European data residency | ✓ `europe-west2` endpoint available | Partial — US-primary |
| Cost (input tokens) | Gemini Flash: very low; Pro: moderate | Sonnet: moderate |
| Multimodal (lab report images) | ✓ Gemini Vision | ✓ Claude vision |

## Decision

**Use Vertex AI (Gemini Pro) as the primary model.** Reasons:
1. GCP-native IAM eliminates a credential management problem — Cloud Run service accounts get Vertex AI access automatically
2. Gemini Flash is available for high-frequency, lower-stakes calls (onboarding, threshold explanations) at significantly lower cost
3. Gemini 1.5 Pro's 1M context window is useful for passing full seasonal history in recommendation calls
4. Stays within the GCP ecosystem (ADR 001)

**Claude API as a documented optional fallback** for the `ai-recommendations` service specifically, if:
- Gemini recommendation quality on a specific task proves insufficient
- A domain expert evaluating the app finds Claude's agricultural reasoning better for their use case
- The operator prefers Anthropic for policy/compliance reasons

The `ai-recommendations` service is deliberately abstracted behind a `get_vertex_client()` / `call_gemini()` pattern — swapping the model requires changing only those two functions, not the prompts or API endpoints.

## What Data Centres Actually Affect

Data centre proximity matters for:
- **Sensor ingestion latency** (Pub/Sub → Cloud Run) — GCP europe-west2 is optimal here
- **Dashboard load time** — BigQuery and Cloud Run in the same region
- **GDPR compliance** — EU farmer data must stay in EU regions; both GCP and Anthropic have EU endpoints

It does **not** meaningfully affect the quality of a 2–3 second AI recommendation call where the bottleneck is model inference time, not network transit.
