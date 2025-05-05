from pydantic import BaseModel
from typing import Optional, List

class Location(BaseModel):
    latitude: float
    longitude: float

class Alert(BaseModel):
    message_id: str
    sensor_id: str
    location: Location
    timestamp: int
    sound_type: str
    confidence: float
    first_timestamp: Optional[int] = None
    processed_at: Optional[int] = None
    category: Optional[str] = None
    intensity: Optional[float] = None

class TrackingLocation(BaseModel):
    latitude: float
    longitude: float
    timestamp: int

class Prediction(BaseModel):
    sensor_id: str
    estimated_arrival_time: int

class Tracking(BaseModel):
    sound_type: str
    locations: List[TrackingLocation]
    speed: float
    direction: float
    predictions: List[Prediction]
