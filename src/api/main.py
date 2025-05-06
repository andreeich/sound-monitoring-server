from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from src.services.mqtt_service import MQTTService
from src.config.database import db

load_dotenv()

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # Client's origin (Vite)
    "http://localhost:5173",  # Default Vite port (if still used)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Existing routes
@app.get("/alerts")
async def get_alerts():
    alerts = list(db.alerts.find({}, {"_id": 0}))  # Exclude MongoDB's _id field
    return alerts

@app.get("/sensors")
async def get_sensors():
    sensors = list(db.sensors.find({}, {"_id": 0}))
    return sensors

@app.get("/trackings")
async def get_trackings():
    trackings = list(db.trackings.find({}, {"_id": 0}))
    return trackings

@app.post("/sensors/register")
async def register_sensor(sensor: dict):
    db.sensors.update_one(
        {"sensor_id": sensor["sensor_id"]},
        {"$set": sensor},
        upsert=True
    )
    return {"status": "Sensor registered"}

# Initialize MQTT service
mqtt_service = MQTTService()

@app.on_event("startup")
async def startup_event():
    mqtt_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_service.stop()
