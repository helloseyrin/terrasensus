"""
TerraSensus — Lab Report Parser
Triggered by GCS upload events. Extracts structured soil data from lab report PDFs/images.
Primary: Google Cloud Document AI. Fallback: Gemini Vision.
"""
from fastapi import FastAPI

app = FastAPI(title="TerraSensus Lab Parser Service")


@app.get("/health")
def health():
    return {"status": "ok", "service": "lab-parser"}


# TODO: POST /parse — accepts GCS URI, returns structured lab report schema
# TODO: Document AI extraction pipeline
# TODO: Gemini Vision fallback for unstructured/scanned documents
# TODO: Normalise output to standard schema regardless of lab format
