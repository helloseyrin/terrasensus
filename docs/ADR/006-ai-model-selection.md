# ADR 006 — AI Model Selection and Resilience Architecture

**Date:** 2026-03-16
**Status:** Accepted — multi-model fallback chain with agronomic bounds validation

---

## Context

TerraSensus may be used by farmers in food-security-critical contexts — Ukrainian wheat fields, Central Asian cotton farms, smallholder operations where a wrong recommendation or a missed alert could mean crop failure. This raises the reliability bar significantly beyond a typical SaaS product.

Two distinct failure modes must be treated separately:

1. **Provider outage** — the AI API is unreachable or returns an error
2. **Model incorrectness** — the AI is available but returns agronomically wrong advice

These require different mitigations.

---

## Provider Uptime — Honest Assessment

No AI provider publishes food-security-grade SLAs. Published figures:

| Provider | Published SLA | Notes |
|---|---|---|
| Vertex AI (Gemini Pro) | 99.95% infrastructure | Covers API availability, not model correctness |
| Anthropic Claude API | No public SLA (standard tier) | Enterprise tier has SLA — unpublished |
| OpenAI GPT-4 | 99.9% (enterprise) | US-primary infrastructure |

99.95% uptime = ~4.4 hours downtime per year. For a farmer checking soil before an irrigation decision, a 2-hour outage at the wrong moment matters.

**Conclusion**: no single provider is reliable enough for a food-security context. The architecture must not depend on any one model being available.

---

## Decision: Multi-Model Fallback Chain

```
Request arrives at /onboarding or /recommend
        │
        ▼ [1] Primary: Vertex AI (Gemini Pro)
        │   timeout: 8s
        │   If fails → log incident → try next
        │
        ▼ [2] Fallback: Claude Sonnet (Anthropic API)
        │   timeout: 8s
        │   Different provider, different infrastructure, different failure modes
        │   If fails → log incident → try next
        │
        ▼ [3] Final fallback: Rule-based knowledge base (local, no external API)
            Always available. Returns structured explanation derived from
            CROP_THRESHOLDS + agronomic reference data embedded in the service.
            Clearly labelled: "AI service temporarily unavailable —
            showing guideline-based recommendation."
```

**Why two external providers**: Gemini and Claude run on entirely separate infrastructure (Google vs Amazon/AWS). A GCP regional incident that takes down Vertex AI will not affect Anthropic's API. This is the standard pattern for critical systems — diversify infrastructure, not just endpoints.

**Why a local fallback**: internet connectivity in rural farming regions is unreliable. A local fallback that requires no external call guarantees the farmer always receives something useful.

---

## Model Correctness — Agronomic Bounds Validation

Uptime is the easier problem. Correctness is harder.

An AI can be available and return plausible-sounding but agronomically harmful advice. Example failure: "apply 400 kg/ha of nitrogen to your wheat field" — this is 2–3× the safe maximum and would cause severe EC buildup and root burn. A confident, well-formatted AI response with a wrong number.

**Mitigation: agronomic bounds checker** — every numeric recommendation from any AI model is validated against hard limits before it reaches the farmer:

```python
AGRONOMIC_BOUNDS = {
    "nitrogen_application_kg_ha":    (0, 250),   # never recommend >250 kg/ha N
    "phosphorus_application_kg_ha":  (0, 120),
    "potassium_application_kg_ha":   (0, 200),
    "ph_target":                     (4.5, 8.5), # outside this: reject response
    "ec_safe_ceiling_ds_m":          (0.0, 5.0),
}
```

If a model output contains a value outside bounds: reject the response, fall back to next model, log the anomaly as an AI quality issue (GitHub issue template exists for this).

---

## Model Correctness — Uncertainty Expression

Every AI response must include an explicit uncertainty statement. The onboarding prompt instructs Gemini/Claude to:
- State when a recommendation is based on general agronomic literature vs region-specific data
- Flag when the input values are unusual or outside the model's confident range
- Never present a recommendation as certain when the underlying data is sparse

The onboarding prompt includes: *"If you are uncertain about any recommendation for this specific region or variety, say so explicitly. Uncertainty expressed honestly is more valuable than false confidence."*

---

## The Non-Negotiable Layer: Rule-Based Alerts

The alert engine (`services/alert-engine/rules.py`) **never calls an AI**. It evaluates thresholds synchronously, locally, with no network dependency. A farmer with no internet, a dead phone signal, or during a 6-hour GCP outage still receives:

- Critical moisture alerts (prevent crop death from drought)
- Critical EC alerts (prevent irreversible salt damage)
- Critical pH alerts (prevent nutrient lockout)
- Drought risk scoring (Open-Meteo is the only external call — can be cached)

The rule-based layer is the safety net. The AI layer is the intelligence layer on top of it. These must never be conflated.

---

## Labelling Requirements

Every AI-generated recommendation displayed to a farmer must include:

1. Which model generated it (Gemini / Claude / Rule-based fallback)
2. The timestamp of generation
3. A persistent disclaimer: *"This recommendation is AI-generated guidance. For decisions affecting food security or significant financial investment, consult a qualified agronomist."*
4. A one-tap "flag this recommendation" button that creates a GitHub issue via the `ai-quality` template

---

## Caching for Offline Resilience

Onboarding responses and the most recent recommendation per plot are cached:
- **Server-side**: 24-hour TTL in Cloud SQL, served from cache if model unavailable
- **Client-side**: React Native AsyncStorage — last known recommendation survives app restart and offline use
- **Displayed with**: "Last updated X ago" label when serving cached content

---

## Implementation Stack

```
services/ai-recommendations/
├── client.py          ← multi-model client with fallback chain + bounds validation
├── fallback.py        ← rule-based local knowledge base (no external API)
├── bounds.py          ← agronomic bounds checker
└── main.py            ← endpoints (unchanged interface regardless of which model responds)
```

---

## What This Does Not Solve

- **Domain expert validation of thresholds**: all `CROP_THRESHOLDS` values are flagged `⚠ UNVALIDATED`. No amount of model redundancy fixes agronomically wrong baseline thresholds. Expert review is required before production deployment in food-security contexts.
- **Hallucination of crop-specific facts**: LLMs can confidently state incorrect agronomic facts. The bounds checker catches dangerous numeric values but cannot catch subtly wrong qualitative advice (e.g. "cotton thrives in waterlogged soil" — false, but not a numeric value to bound-check). This is mitigated by labelling and the agronomist disclaimer, not by code.
- **Real-time sensor accuracy**: if the sensors themselves are miscalibrated, no AI can compensate. Sensor maintenance logs (phase 2) and periodic lab report cross-referencing are the mitigations.
