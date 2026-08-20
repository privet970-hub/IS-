"""Vehicle Models"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class VehicleType(str, Enum):
    """Vehicle type enumeration"""
    SMALL = "small"      # < 3.5 tons
    MEDIUM = "medium"    # 3.5 - 10 tons
    LARGE = "large"      # 10 - 25 tons
    XLARGE = "xlarge"    # > 25 tons


class Vehicle(BaseModel):
    """Vehicle information"""
    id: str = Field(..., description="Unique vehicle identifier")
    name: str = Field(..., description="Vehicle name/plate number")
    vehicle_type: VehicleType = Field(..., description="Vehicle type")
    capacity: float = Field(..., description="Maximum capacity (kg)")
    fuel_consumption: float = Field(..., description="Fuel consumption (L/100km)")
    fuel_cost_per_liter: float = Field(..., description="Fuel cost per liter (KRW)")
    max_driving_hours: int = Field(default=10, description="Maximum driving hours per day")
    start_location_id: str = Field(..., description="Starting location ID")
    end_location_id: Optional[str] = Field(None, description="Ending location ID (if different)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "v_001",
                "name": "Large Truck #001",
                "vehicle_type": "large",
                "capacity": 20000,
                "fuel_consumption": 8.5,
                "fuel_cost_per_liter": 1500,
                "start_location_id": "loc_001",
            }
        }
