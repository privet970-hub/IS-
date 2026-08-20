"""Location and Route Models"""
from pydantic import BaseModel, Field
from typing import Optional, List


class Location(BaseModel):
    """Location with coordinates"""
    id: str = Field(..., description="Unique location identifier")
    name: str = Field(..., description="Location name")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "loc_001",
                "name": "Seoul Distribution Center",
                "latitude": 37.4979,
                "longitude": 127.0276,
            }
        }


class Stop(Location):
    """Delivery or pickup stop"""
    arrival_time: Optional[int] = Field(None, description="Time window start (seconds from midnight)")
    departure_time: Optional[int] = Field(None, description="Time window end (seconds from midnight)")
    demand: float = Field(default=0, description="Weight/volume demanded at this location (kg)")
    service_time: int = Field(default=0, description="Service time required (seconds)")
