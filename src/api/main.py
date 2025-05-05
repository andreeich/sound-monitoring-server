from fastapi import FastAPI
from src.services.mqtt_service import MQTTService
from src.config.database import db
from src.models.alert import Alert, Tracking
from typing import List
import uvicorn

app = FastAPI(title="Sound Monitoring API")
mqtt_service = MQTTService()

@app.on_event("startup")
async def startup_event():
    mqtt_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_service.stop()
    db.close()

@app.get("/alerts", response_model=List[Alert])
async def get_alerts():
    alerts = list(db.alerts.find({}, {"_id": 0}))
    return alerts

@app.get("/sensors")
async def get_sensors():
    sensors = list(db.sensors.find({}, {"_id": 0}))
    return sensors

@app.get("/trackings", response_model=List[Tracking])
async def get_trackings():
    trackings = list(db.trackings.find({}, {"_id": 0}))
    return trackings

@app.post("/sensors/register")
async def register_sensor(sensor: dict):
    db.sensors.update_one(
        {"sensor_id": sensor["sensor_id"]},
        {
            "$set": {
                "location": sensor["location"],
                "last_seen": int(__import__("time").time() * 1000),
                "status": "online"
            }
        },
        upsert=True
    )
    return {"success": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
