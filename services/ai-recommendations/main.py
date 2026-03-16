"""
TerraSensus — AI Recommendations Service
Uses Vertex AI (Gemini Pro) to generate crop, fertiliser, and eco-scored supplier recommendations.
"""
from fastapi import FastAPI

app = FastAPI(title="TerraSensus AI Recommendations Service")


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-recommendations"}


# TODO: POST /recommend — accepts soil profile + crop intent, returns Gemini recommendation
# TODO: POST /suppliers — accepts nutrient deficiencies + region, returns eco-scored supplier list
# TODO: POST /interpret-lab — accepts structured lab report, returns plain-language interpretation
