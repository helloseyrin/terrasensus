# Engineering Notes — AI Recommendations

---

## Hybrid alert strategy

The system uses two separate intelligence layers, each suited to a different task:

| Layer | Technology | Use case | Latency |
|---|---|---|---|
| Rule engine | Python (`rules.py`) | Critical threshold alerts | <1ms |
| AI layer | Vertex AI (Gemini Pro) | Deep soil analysis, supplier recommendations | 2–5s |

The rule engine fires instantly and synchronously — a farmer gets a push notification the moment moisture hits critical low. The AI layer runs on-demand (farmer taps "Get Recommendations") and returns nuanced natural-language analysis. Never use the AI layer for critical alerts — latency and occasional model errors make it unsuitable for time-sensitive warnings.

## Ecological scoring in supplier recommendations

The supplier recommendation prompt instructs Gemini to rank options by a composite of three signals:
1. **Effectiveness** — does it address the specific deficiency?
2. **Eco-score** — organic/slow-release preferred, especially when EC is already high
3. **Cost-effectiveness** — estimated cost per hectare

EC level is explicitly passed in the prompt. High EC is a signal to *avoid* high-N synthetic fertilisers (they worsen salt buildup), so the model should automatically downrank them. This is a prompt-level constraint, not a hard filter — it preserves model flexibility for unusual edge cases.

## Prompt versioning

Prompts live in `services/ai-recommendations/prompts/` and are treated as first-class code artifacts — they go through code review and are versioned in git. Changes to prompts should be evaluated against a set of known soil profiles with expected outputs before merging.

## Gemini Vision for lab report parsing

Cloud Document AI handles structured, machine-generated PDFs well. For scanned or photographed lab reports (common when farmers photograph a paper report), Document AI's form parser degrades significantly. Gemini Vision is used as a fallback: the PDF/image is passed directly to Gemini with a structured extraction prompt, and the output is normalised to the same `LabResults` schema regardless of which parser was used.
