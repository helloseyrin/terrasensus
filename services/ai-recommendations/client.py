"""
TerraSensus — Multi-Model AI Client

Implements a fallback chain for food-security resilience:
  1. Vertex AI (Gemini Pro) — GCP-native, primary
  2. Claude Sonnet (Anthropic API) — separate infrastructure, fallback
  3. Rule-based local knowledge base — always available, final fallback

Every response is validated against agronomic bounds before reaching the farmer.
Every failure is logged for post-incident review.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModelSource(str, Enum):
    GEMINI = "gemini-1.5-pro"
    CLAUDE = "claude-sonnet-4-6"
    RULE_BASED = "rule-based-fallback"


@dataclass
class AIResponse:
    content: dict
    source: ModelSource
    latency_ms: int
    cached: bool = False


# ── Agronomic bounds checker ──────────────────────────────────────────────────

# Hard limits: any AI numeric recommendation outside these ranges is rejected.
# Values are conservative maximums — err on the side of caution.
# ⚠ UNVALIDATED — require agronomist review before production.
AGRONOMIC_BOUNDS: dict[str, tuple[float, float]] = {
    "nitrogen_application_kg_ha":   (0, 250),
    "phosphorus_application_kg_ha": (0, 120),
    "potassium_application_kg_ha":  (0, 200),
    "ph_target":                    (4.0, 9.0),
    "ec_safe_ceiling_ds_m":         (0.0, 6.0),
    "moisture_target_pct":          (0.0, 100.0),
}


def check_bounds(response: dict) -> list[str]:
    """
    Scan a response dict recursively for numeric values that exceed agronomic bounds.
    Returns a list of violation descriptions (empty = safe).
    """
    violations = []
    for key, (lo, hi) in AGRONOMIC_BOUNDS.items():
        value = _find_value(response, key)
        if value is not None:
            try:
                v = float(value)
                if not (lo <= v <= hi):
                    violations.append(
                        f"{key}={v} outside safe range [{lo}, {hi}]"
                    )
            except (TypeError, ValueError):
                pass
    return violations


def _find_value(obj, key: str):
    """Recursively search a nested dict/list for a key."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            result = _find_value(v, key)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _find_value(item, key)
            if result is not None:
                return result
    return None


# ── Model clients ─────────────────────────────────────────────────────────────

def _call_gemini(prompt: str, timeout: int = 8) -> dict:
    """Call Vertex AI Gemini Pro. Raises on failure."""
    import vertexai
    from vertexai.generative_models import GenerativeModel

    project = os.environ["VERTEX_AI_PROJECT"]
    location = os.getenv("VERTEX_AI_LOCATION", "europe-west2")
    vertexai.init(project=project, location=location)

    model = GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"},
        # Vertex AI does not have a direct timeout param in SDK —
        # wrap in asyncio with timeout or use grpc deadline in production
    )
    return json.loads(response.text)


def _call_claude(prompt: str, timeout: int = 8) -> dict:
    """Call Anthropic Claude Sonnet. Raises on failure."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{prompt}\n\n"
                    "Respond with valid JSON only. No markdown fences, no commentary."
                ),
            }
        ],
        timeout=timeout,
    )
    return json.loads(message.content[0].text)


# ── Rule-based fallback ───────────────────────────────────────────────────────

def _rule_based_onboarding(context: dict) -> dict:
    """
    Generates a structured onboarding response from local agronomic knowledge.
    No external API call — always available.
    Intentionally conservative and general. Labelled clearly as rule-based.
    """
    crop = context.get("crop", "your crop")
    region = context.get("region", "your region")
    farmer = context.get("farmer_name", "Farmer").split()[0]
    ec = context.get("ec", 0)
    ph = context.get("ph", 7.0)
    nitrogen = context.get("nitrogen", 50)

    watch_list = [
        {
            "sensor": "ec",
            "why_it_matters": "EC measures salt accumulation — high levels lock out nutrients and damage roots.",
            "what_to_watch_for": "EC rising above 2.0 dS/m over consecutive readings.",
            "plain_english_range": "Most crops are comfortable below 2.0 dS/m. Above 3.0 is critical for most.",
        },
        {
            "sensor": "ph",
            "why_it_matters": "pH controls which nutrients are available to roots, regardless of how much is in the soil.",
            "what_to_watch_for": "pH drifting outside the 5.5–7.5 range over weeks.",
            "plain_english_range": "Most crops prefer 6.0–7.0. Outside this, nutrients become chemically unavailable.",
        },
        {
            "sensor": "nitrogen",
            "why_it_matters": "Nitrogen drives leaf and stem growth. Too little means poor yield; too much wastes money and raises EC.",
            "what_to_watch_for": "Nitrogen declining steadily over the growing season without replenishment.",
            "plain_english_range": "Healthy range varies by crop — your TerraSensus dashboard shows your crop-specific target.",
        },
    ]

    ec_note = ""
    if ec >= 2.0:
        ec_note = f" Your current EC ({ec} dS/m) is already elevated — monitor closely and avoid synthetic fertilisers until it drops."

    return {
        "welcome_message": (
            f"Welcome, {farmer}. Your {crop} plot in {region} is now registered with TerraSensus. "
            f"We'll monitor your soil continuously and alert you to anything that needs attention."
        ),
        "soil_portrait": (
            f"This is a guideline-based overview while our AI service is temporarily unavailable. "
            f"For {crop} in {region}, focus on maintaining stable pH and avoiding EC buildup. "
            f"Full AI-personalised profile will be generated when the service recovers."
        ),
        "current_reading_interpretation": (
            f"Your current readings: pH {ph}, N {nitrogen} mg/kg, EC {ec} dS/m.{ec_note} "
            f"A full personalised interpretation will be available when AI service recovers."
        ),
        "watch_list": watch_list,
        "regional_risk": (
            f"Specific regional risk analysis for {region} requires AI service. "
            f"General risk: monitor EC if using irrigation or synthetic fertilisers."
        ),
        "one_thing_to_learn": (
            "Electrical Conductivity (EC) is the single most useful number for understanding "
            "fertiliser impact. It measures dissolved salts — every synthetic fertiliser application "
            "raises it slightly. Over time, without leaching rain or irrigation, it accumulates to "
            "levels that physically block roots from absorbing water. Watching your EC trend is "
            "the fastest way to understand if your fertiliser practice is sustainable."
        ),
        "regenerative_note": (
            "Cover crops between main crop cycles naturally cycle nutrients and suppress weeds "
            "without raising EC — a low-risk starting point for any farming style."
        ),
    }


# ── Main fallback chain ───────────────────────────────────────────────────────

def generate_with_fallback(
    prompt: str,
    context: dict,
    call_type: str = "general",
) -> AIResponse:
    """
    Attempt to generate a response using the fallback chain:
      1. Gemini Pro (Vertex AI)
      2. Claude Sonnet (Anthropic)
      3. Rule-based local fallback

    All responses are bounds-checked before being returned.
    Failures are logged with enough context for post-incident review.

    Args:
        prompt:     formatted prompt string
        context:    raw context dict (used by rule-based fallback + bounds check)
        call_type:  label for logging ("onboarding", "recommend", "supplier", etc.)
    """
    env = os.getenv("ENV", "development")

    attempts = []
    if env != "development":
        attempts = [
            ("gemini", _call_gemini),
            ("claude", _call_claude),
        ]

    for model_name, caller in attempts:
        start = time.monotonic()
        try:
            result = caller(prompt)
            latency_ms = int((time.monotonic() - start) * 1000)

            violations = check_bounds(result)
            if violations:
                logger.error(
                    f"[{call_type}] {model_name} response failed bounds check: {violations}. "
                    f"Falling back to next model."
                )
                continue

            source = ModelSource.GEMINI if model_name == "gemini" else ModelSource.CLAUDE
            logger.info(f"[{call_type}] {model_name} succeeded in {latency_ms}ms")
            return AIResponse(content=result, source=source, latency_ms=latency_ms)

        except Exception as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            logger.error(
                f"[{call_type}] {model_name} failed after {latency_ms}ms: {e}. "
                f"Trying next model."
            )
            continue

    # Final fallback — always succeeds
    logger.warning(
        f"[{call_type}] All AI models failed or unavailable. "
        f"Serving rule-based fallback response."
    )
    if call_type == "onboarding":
        result = _rule_based_onboarding(context)
    else:
        result = {
            "status": "rule-based-fallback",
            "message": (
                "AI recommendations temporarily unavailable. "
                "Your critical alerts remain active. "
                "Please check back shortly for full recommendations."
            ),
        }

    return AIResponse(
        content=result,
        source=ModelSource.RULE_BASED,
        latency_ms=0,
    )
