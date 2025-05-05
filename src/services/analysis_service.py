from math import sin, cos, sqrt, atan2, radians
from src.config.database import db
import time

def categorize_sound_type(sound_type: str) -> str:
    categories = {
        "drone": "air",
        "quadcopter": "air",
        "siren": "emergency",
        "chainsaw": "ground"
    }
    for key, category in categories.items():
        if key in sound_type.lower():
            return category
    return "other"

def calculate_intensity(confidence: float) -> float:
    return min(10.0, max(0.0, confidence / 10.0))

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000  # Радіус Землі в метрах
    φ1 = radians(lat1)
    φ2 = radians(lat2)
    Δφ = radians(lat2 - lat1)
    Δλ = radians(lon2 - lon1)

    a = sin(Δφ / 2) * sin(Δφ / 2) + cos(φ1) * cos(φ2) * sin(Δλ / 2) * sin(Δλ / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c  # Відстань у метрах

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    φ1 = radians(lat1)
    φ2 = radians(lat2)
    Δλ = radians(lon2 - lon1)

    y = sin(Δλ) * cos(φ2)
    x = cos(φ1) * sin(φ2) - sin(φ1) * cos(φ2) * cos(Δλ)

    bearing = atan2(y, x) * 180 / 3.141592653589793
    return (bearing + 360) % 360

def update_tracking(alert: dict):
    sound_type = alert["sound_type"].lower()
    MAX_AGE = 10 * 60 * 1000  # 10 хвилин
    SPEED_THRESHOLD = 1  # 1 м/с

    # Отримання або створення трекінгу
    tracking = db.trackings.find_one({"sound_type": sound_type})
    if not tracking:
        tracking = {
            "sound_type": sound_type,
            "locations": [],
            "speed": 0.0,
            "direction": 0.0,
            "predictions": []
        }

    # Додавання нової локації
    tracking["locations"].append({
        "latitude": alert["location"]["latitude"],
        "longitude": alert["location"]["longitude"],
        "timestamp": alert["timestamp"]
    })

    # Видалення старих локацій
    now = int(time.time() * 1000)
    tracking["locations"] = [
        loc for loc in tracking["locations"] if (now - loc["timestamp"]) <= MAX_AGE
    ]

    # Обмеження кількості локацій
    if len(tracking["locations"]) > 100:
        tracking["locations"] = tracking["locations"][-100:]

    # Розрахунок швидкості та напрямку
    if len(tracking["locations"]) >= 2:
        prev_loc, curr_loc = tracking["locations"][-2:]
        time_diff = (curr_loc["timestamp"] - prev_loc["timestamp"]) / 1000

        if time_diff > 0:
            distance = calculate_distance(
                prev_loc["latitude"], prev_loc["longitude"],
                curr_loc["latitude"], curr_loc["longitude"]
            )
            tracking["speed"] = distance / time_diff
            tracking["direction"] = calculate_bearing(
                prev_loc["latitude"], prev_loc["longitude"],
                curr_loc["latitude"], curr_loc["longitude"]
            )

    # Прогнозування
    if tracking["speed"] > SPEED_THRESHOLD:
        tracking["predictions"] = []
        for sensor in db.sensors.find({"sensor_id": {"$ne": alert["sensor_id"]}}):
            distance = calculate_distance(
                alert["location"]["latitude"], alert["location"]["longitude"],
                sensor["location"]["latitude"], sensor["location"]["longitude"]
            )
            if tracking["speed"] > 0:
                time_to_arrival = distance / tracking["speed"]
                if time_to_arrival < 30 * 60:  # Менше 30 хвилин
                    tracking["predictions"].append({
                        "sensor_id": sensor["sensor_id"],
                        "estimated_arrival_time": now + int(time_to_arrival * 1000)
                    })

        tracking["predictions"].sort(key=lambda x: x["estimated_arrival_time"])

    # Збереження трекінгу
    db.trackings.update_one(
        {"sound_type": sound_type},
        {"$set": tracking},
        upsert=True
    )
