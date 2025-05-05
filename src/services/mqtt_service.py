import paho.mqtt.client as mqtt
import json
import os
from dotenv import load_dotenv
from src.config.database import db
from src.services.analysis_service import categorize_sound_type, calculate_intensity, update_tracking

load_dotenv()

class MQTTService:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.broker = os.getenv("MQTT_BROKER")

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with code {rc}")
        self.client.subscribe("sound_monitoring/sensor/+/alert")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            alert = {
                "message_id": payload["message_id"],
                "sensor_id": payload["sensor_id"],
                "location": payload["location"],
                "timestamp": payload["timestamp"],
                "sound_type": payload["sound_type"],
                "confidence": payload["confidence"],
                "first_timestamp": payload.get("first_timestamp", payload["timestamp"]),
                "processed_at": int(__import__("time").time() * 1000),
                "category": categorize_sound_type(payload["sound_type"]),
                "intensity": calculate_intensity(payload["confidence"])
            }
            # Збереження сповіщення
            db.alerts.insert_one(alert)
            print(f"Saved alert: {alert}")

            # Оновлення сенсора
            db.sensors.update_one(
                {"sensor_id": alert["sensor_id"]},
                {
                    "$set": {
                        "location": alert["location"],
                        "last_seen": int(__import__("time").time() * 1000),
                        "status": "online"
                    }
                },
                upsert=True
            )

            # Оновлення відстеження
            update_tracking(alert)

            # Відправка підтвердження
            client.publish(
                f"sound_monitoring/sensor/{alert['sensor_id']}/ack",
                json.dumps({"message_id": alert["message_id"], "status": "received"})
            )

        except Exception as e:
            print(f"Error processing message: {e}")

    def start(self):
        self.client.connect(self.broker.replace("mqtt://", "").split(":")[0], 1883, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
