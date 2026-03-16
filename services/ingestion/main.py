"""
TerraSensus — Ingestion Service
Receives sensor readings from GCP Pub/Sub and writes to Cloud SQL.
"""
from fastapi import FastAPI

app = FastAPI(title="TerraSensus Ingestion Service")


@app.get("/health")
def health():
    return {"status": "ok", "service": "ingestion"}


# TODO: Pub/Sub push subscription endpoint
# TODO: Sensor reading validation + Cloud SQL write
# TODO: Trigger Datastream sync to BigQuery
