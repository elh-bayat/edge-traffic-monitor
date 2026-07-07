from pydantic import BaseModel, Field
from datetime import datetime


class TrafficReading(BaseModel):
    """The data shape we expect from each camera."""
    camera_id: str = Field(..., example="cam_01")
    location: str
    timestamp: datetime
    vehicle_count: int = Field(..., ge=0, le=500)   # must be 0–500
    average_speed_kmh: float = Field(..., ge=0.0, le=300.0)
    weather: str


class TrafficReadingResponse(BaseModel):
    """What we send back after accepting a reading."""
    message: str
    camera_id: str
    received_at: datetime
