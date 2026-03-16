"""
TerraSensus — Alert Engine
Evaluates sensor readings against thresholds and triggers Firebase push notifications.
"""
from fastapi import FastAPI

app = FastAPI(title="TerraSensus Alert Engine")


@app.get("/health")
def health():
    return {"status": "ok", "service": "alert-engine"}


# TODO: Subscribe to ingestion events
# TODO: Evaluate rules from rules.py
# TODO: Drought risk evaluation via drought.py
# TODO: Send FCM push notification on critical alert
