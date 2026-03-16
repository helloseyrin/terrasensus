"""
TerraSensus — AI Recommendations Service

Endpoints:
  POST /onboarding/{plot_id}     Crop-aware soil education at plot registration
  POST /recommend/{plot_id}      Full soil health recommendation for a plot
  POST /suppliers/{plot_id}      Eco-scored fertiliser supplier suggestions
  POST /regenerative/{plot_id}   Regenerative alternatives to synthetic inputs
  POST /interpret-lab/{report_id} Plain-English lab report interpretation
"""

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="TerraSensus AI Recommendations Service")

PROMPTS_DIR = Path(__file__).parent / "prompts"


# ── Request / Response models ─────────────────────────────────────────────────

class PlotContext(BaseModel):
    plot_id: str
    farmer_name: str
    region: str
    crop: str
    variety: str
    area_ha: float
    climate_zone: str
    farming_style: str
    moisture: float
    temperature: float
    ph: float
    nitrogen: float
    phosphorus: float
    potassium: float
    ec: float


class OnboardingResponse(BaseModel):
    plot_id: str
    welcome_message: str
    soil_portrait: str
    current_reading_interpretation: str
    watch_list: list[dict]
    regional_risk: str
    one_thing_to_learn: str
    regenerative_note: str
    crop_thresholds: dict          # crop-aware thresholds returned for frontend display


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.txt").read_text()


def get_vertex_client():
    """
    Returns a Vertex AI GenerativeModel client.
    Returns None in development mode (ENV != production) so stubs are used.
    """
    env = os.getenv("ENV", "development")
    if env == "development":
        return None
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        project = os.getenv("VERTEX_AI_PROJECT")
        location = os.getenv("VERTEX_AI_LOCATION", "europe-west2")
        vertexai.init(project=project, location=location)
        return GenerativeModel("gemini-1.5-pro")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Vertex AI unavailable: {e}")


def call_gemini(model, prompt: str) -> dict:
    """Call Gemini and parse JSON response."""
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    return json.loads(response.text)


def stub_onboarding(ctx: PlotContext) -> dict:
    """
    Development stub — returns realistic-looking onboarding data without
    calling Vertex AI. Replace with real call once GCP credentials are set.
    """
    return {
        "welcome_message": (
            f"Welcome to TerraSensus, {ctx.farmer_name.split()[0]}! "
            f"We're glad to have your {ctx.crop.replace('_', ' ')} plot in {ctx.region} on board."
        ),
        "soil_portrait": (
            f"[STUB] Healthy soil for {ctx.crop} in {ctx.region} — "
            "connect Vertex AI credentials to generate a real profile."
        ),
        "current_reading_interpretation": (
            f"[STUB] Your current baseline: pH {ctx.ph}, N {ctx.nitrogen} mg/kg, "
            f"EC {ctx.ec} dS/m. Real interpretation requires Vertex AI."
        ),
        "watch_list": [
            {
                "sensor": "ec",
                "why_it_matters": "[STUB] EC indicates salt accumulation.",
                "what_to_watch_for": "[STUB] Rising EC after irrigation.",
                "plain_english_range": "[STUB] Requires Vertex AI for crop-specific range.",
            }
        ],
        "regional_risk": f"[STUB] Regional risk for {ctx.region} — requires Vertex AI.",
        "one_thing_to_learn": "[STUB] Set VERTEX_AI_PROJECT to enable real AI responses.",
        "regenerative_note": "[STUB] Regenerative suggestion — requires Vertex AI.",
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-recommendations"}


@app.post("/onboarding/{plot_id}", response_model=OnboardingResponse)
def plot_onboarding(plot_id: str, ctx: PlotContext):
    """
    Called when a farmer registers a new plot.
    Returns crop-aware soil education, threshold explanations, and regional risk
    summary — all personalised to their crop and region via Gemini.

    Also returns the crop-aware threshold values so the mobile app can display
    "your healthy N range is 15–60 mg/kg" rather than global defaults.
    """
    from services.alert_engine.rules import get_thresholds  # local import to avoid circular

    # Get crop-aware thresholds to include in response
    crop_thresholds = get_thresholds(ctx.crop)

    model = get_vertex_client()

    if model is None:
        # Development mode — return stub
        ai_response = stub_onboarding(ctx)
    else:
        template = load_prompt("plot_onboarding")
        prompt = template.format(
            farmer_name=ctx.farmer_name,
            region=ctx.region,
            crop=ctx.crop,
            variety=ctx.variety,
            area_ha=ctx.area_ha,
            climate_zone=ctx.climate_zone,
            farming_style=ctx.farming_style,
            moisture=ctx.moisture,
            temperature=ctx.temperature,
            ph=ctx.ph,
            nitrogen=ctx.nitrogen,
            phosphorus=ctx.phosphorus,
            potassium=ctx.potassium,
            ec=ctx.ec,
        )
        ai_response = call_gemini(model, prompt)

    return OnboardingResponse(
        plot_id=plot_id,
        crop_thresholds=crop_thresholds,
        **ai_response,
    )


@app.post("/recommend/{plot_id}")
def recommend(plot_id: str, ctx: PlotContext):
    """
    Full soil health recommendation for a plot.
    Called on-demand by the farmer from the recommendations screen.
    """
    # TODO: wire up soil_recommendation.txt prompt + Gemini call
    return {"plot_id": plot_id, "status": "stub — implement with Vertex AI"}


@app.post("/suppliers/{plot_id}")
def suppliers(plot_id: str, ctx: PlotContext):
    """
    Eco-scored fertiliser supplier recommendations based on current deficiencies.
    """
    # TODO: wire up supplier_recommendation.txt prompt + Gemini call
    return {"plot_id": plot_id, "status": "stub — implement with Vertex AI"}


@app.post("/regenerative/{plot_id}")
def regenerative(plot_id: str, ctx: PlotContext):
    """
    Regenerative alternatives to synthetic fertilisers for this crop and region.
    """
    # TODO: wire up regenerative_alternatives.txt prompt + Gemini call
    return {"plot_id": plot_id, "status": "stub — implement with Vertex AI"}
