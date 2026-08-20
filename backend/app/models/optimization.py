"""Optimization Request and Response Models"""
from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.location import Stop
from app.models.vehicle import Vehicle


class OptimizationRequest(BaseModel):
    """Route optimization request"""
    vehicles: List[Vehicle] = Field(..., description="List of available vehicles")
    stops: List[Stop] = Field(..., description="List of delivery/pickup stops")
    start_depot_id: str = Field(..., description="Starting depot location ID")
    end_depot_id: Optional[str] = Field(None, description="Ending depot location ID")
    time_limit_seconds: int = Field(default=30, description="Optimization time limit in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "vehicles": [],
                "stops": [],
                "start_depot_id": "depot_001",
            }
        }


class RouteStop(BaseModel):
    """A stop in the optimized route"""
    stop_id: str
    stop_name: str
    arrival_time: int
    departure_time: int
    demand: float
    cumulative_distance: float
    cumulative_fuel_consumption: float
    cumulative_cost: float


class OptimizedRoute(BaseModel):
    """Single vehicle's optimized route"""
    vehicle_id: str
    vehicle_name: str
    stops: List[RouteStop]
    total_distance: float
    total_fuel_consumption: float
    total_cost: float  # Fuel cost
    total_demand: float
    utilization_rate: float  # Capacity utilization percentage


class OptimizationResponse(BaseModel):
    """Route optimization response"""
    success: bool
    message: str
    routes: List[OptimizedRoute] = Field(default_factory=list)
    total_distance: float = 0
    total_fuel_consumption: float = 0
    total_cost: float = 0
    unserved_stops: List[str] = Field(default_factory=list)
    optimization_time_ms: int = 0
