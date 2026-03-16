# Engineering Notes — AI Recommendations

---

## Hybrid alert strategy

The system uses two separate intelligence layers, each suited to a different task:

| Layer | Technology | Use case | Latency |
|---|---|---|---|
| Rule engine | Python (`rules.py`) | Critical threshold alerts | <1ms |
| AI layer | Vertex AI (Gemini Pro) | Deep soil analysis, supplier recommendations | 2–5s |

The rule engine fires instantly and synchronously — a farmer gets a push notification the moment moisture hits critical low. The AI layer runs on-demand (farmer taps "Get Recommendations") and returns nuanced natural-language analysis. Never use the AI layer for critical alerts — latency and occasional model errors make it unsuitable for time-sensitive warnings.

## Crop-aware thresholds — why global defaults are insufficient

The alert engine in `rules.py` uses a two-layer threshold system: global defaults that apply to any crop, and per-crop overrides that replace specific sensors.

The critical insight is that **the same numeric value can mean something completely different depending on what you're growing**:

| Sensor | Value | Wheat | Cotton | Pinot Noir |
|---|---|---|---|---|
| N (mg/kg) | 38 | warning (low=50) | healthy (low=30) | healthy (low=15) |
| EC (dS/m) | 2.4 | warning (high=2.5) | warning (high=3.5) | **critical** (critical_high=2.0) |
| pH | 7.9 | warning (high=7.5) | healthy (high=8.0) | critical (critical_high=7.5) |

Elena's vineyard running at N=38 mg/kg is intentional and healthy for Pinot Noir — grapes kept N-low produce better fruit quality. If the global threshold (low=30, close call) or wheat threshold (low=50, definite warning) were applied, the system would alert every day on a perfectly well-managed vineyard. This is the false-alarm suppression problem.

Fatima's cotton at EC=2.4 dS/m triggers a warning under both global and cotton thresholds, but the ceiling matters: cotton can tolerate up to 5.0 dS/m before critical (it's why cotton survived the Aral Sea salinisation). Applying global EC thresholds (critical_high=3.0) would generate false critical alerts on a cotton crop that is actually coping.

**Implementation**: `get_thresholds(crop)` in `rules.py` merges `CROP_THRESHOLDS[crop]` onto `THRESHOLDS`. Sensors not overridden by a crop use global defaults. This means you only need to specify the sensors where a crop genuinely differs — a new crop entry doesn't need all 7 sensors.

All crop threshold values are flagged `⚠ UNVALIDATED` in `rules.py` pending agronomist review. See `docs/ai-usage-policy.md` for the validation checklist.

---

## Plot onboarding — the first AI touchpoint

When a farmer registers a new plot, `POST /onboarding/{plot_id}` generates a personalised soil education response before they've seen a single reading. This is the first thing a farmer reads from TerraSensus — it sets their trust calibration for everything that follows.

**What the onboarding response contains** (from `prompts/plot_onboarding.txt`):
- `welcome_message` — 2 sentences, addresses the farmer by first name, acknowledges their specific crop and region
- `soil_portrait` — what healthy soil looks like for this crop in this region (pH, nutrients, regional characteristic)
- `current_reading_interpretation` — plain-English interpretation of their baseline sensor readings
- `watch_list` — 3–4 sensors that matter most for this crop, with why and what to watch for
- `regional_risk` — the single biggest soil health risk in their region for their crop
- `one_thing_to_learn` — one concept explained in plain English to build the farmer's mental model
- `regenerative_note` — one concrete non-chemical practice suited to their crop and region

**Why onboarding is acceptable for AI** (per `docs/ai-usage-policy.md`):
The farmer is not about to act on this content — they are learning context. A wrong fact here is correctable in a follow-up conversation. A wrong threshold alert at 3am is not. Onboarding is educational, not operational.

**Crop thresholds returned alongside AI content**: the `/onboarding` endpoint also calls `get_thresholds(ctx.crop)` and returns the result as `crop_thresholds` in the response. The mobile app uses this to display correct healthy range indicators on each sensor card from day one — the farmer sees "healthy range: 15–60 mg/kg" for their vineyard, not the global "30–150 mg/kg" that would make their N look low.

**Rule-based fallback for onboarding**: if both Gemini and Claude are unavailable, `_rule_based_onboarding()` in `client.py` generates a structured onboarding response from local logic — no external API required. It explicitly tells the farmer this is a guideline response and that a full AI profile will be generated when the service recovers. It also detects elevated EC (≥2.0 dS/m) from the context dict and adds a specific EC warning. The fallback is intentionally conservative and general — it does not attempt to simulate the regional specificity of a real AI response.

**Caching**: onboarding responses are expensive (multi-paragraph generation) and change slowly. Cache in `onboarding_cache` table in Cloud SQL with 30-day TTL, invalidated if crop or region changes. Mobile stores in AsyncStorage with no TTL (serves offline).

**Tone constraints in the prompt**: the prompt explicitly prohibits "it is important to note", requires addressing the farmer as a capable adult, forbids generic advice (must be specific to this crop in this region), and instructs the model to say plainly when something is concerning. These constraints exist because early AI drafts produced condescending, hedged, generic text that farmers would dismiss after reading once.

---

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
