from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# PUBLIC_INTERFACE
class User(BaseModel):
    """Represents a user of the system."""
    id: Optional[str] = Field(default=None, description="MongoDB stringified ObjectId")
    email: EmailStr = Field(..., description="Unique email address")
    name: str = Field(..., description="Full name of the user")
    role: Literal["admin", "researcher", "ranger", "viewer"] = Field(default="viewer", description="Access role")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


# PUBLIC_INTERFACE
class Animal(BaseModel):
    """Represents a tracked animal."""
    id: Optional[str] = Field(default=None)
    species: str = Field(..., description="Species (e.g., 'Sloth Bear')")
    tag_id: str = Field(..., description="Unique collar/tag identifier")
    sex: Optional[Literal["male", "female", "unknown"]] = Field(default="unknown")
    age_years: Optional[float] = Field(default=None, description="Approximate age in years")
    name: Optional[str] = Field(default=None, description="Optional name")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# PUBLIC_INTERFACE
class Device(BaseModel):
    """Represents a tracking device."""
    id: Optional[str] = Field(default=None)
    device_id: str = Field(..., description="Unique device identifier")
    animal_id: Optional[str] = Field(default=None, description="Linked animal id")
    status: Literal["active", "inactive", "maintenance", "retired"] = Field(default="active")
    battery_level: Optional[float] = Field(default=None, description="Battery percentage")
    last_seen_at: Optional[datetime] = Field(default=None, description="Last telemetry timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# PUBLIC_INTERFACE
class TelemetryPoint(BaseModel):
    """A single telemetry datapoint for an animal/device."""
    id: Optional[str] = Field(default=None)
    animal_id: Optional[str] = Field(default=None)
    device_id: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # GeoJSON point for location
    location: dict = Field(
        ..., description="GeoJSON Point: {'type': 'Point', 'coordinates': [lon, lat]}"
    )
    speed_kmh: Optional[float] = Field(default=None)
    heart_rate_bpm: Optional[float] = Field(default=None)
    temperature_c: Optional[float] = Field(default=None)
    extra: Optional[dict] = Field(default=None, description="Additional payload")


# PUBLIC_INTERFACE
class Geofence(BaseModel):
    """A geofence polygon/area."""
    id: Optional[str] = Field(default=None)
    name: str = Field(..., description="Unique geofence name")
    description: Optional[str] = Field(default=None)
    active: bool = Field(default=True)
    # GeoJSON polygon or multipolygon
    geometry: dict = Field(..., description="GeoJSON Polygon/MultiPolygon")
    created_by: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# PUBLIC_INTERFACE
class Alert(BaseModel):
    """An alert triggered by system rules."""
    id: Optional[str] = Field(default=None)
    animal_id: Optional[str] = Field(default=None)
    type: Literal["geofence_breach", "inactivity", "low_battery", "custom"] = Field(default="custom")
    message: str = Field(..., description="Human-readable alert message")
    status: Literal["open", "acknowledged", "resolved"] = Field(default="open")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default=None)


# PUBLIC_INTERFACE
class Sighting(BaseModel):
    """A user-submitted wildlife sighting."""
    id: Optional[str] = Field(default=None)
    species: str = Field(..., description="Reported species")
    reporter_id: Optional[str] = Field(default=None, description="User ID of the reporter")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # GeoJSON point
    location: dict = Field(
        ..., description="GeoJSON Point: {'type': 'Point', 'coordinates': [lon, lat]}"
    )
    notes: Optional[str] = Field(default=None)
    media_urls: Optional[List[str]] = Field(default=None)
    confidence: Optional[float] = Field(default=None, description="Confidence 0..1")
