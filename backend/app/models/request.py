"""Request Models for Maps and Optimization APIs"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CoordinateModel(BaseModel):
    """위치 좌표 모델"""
    latitude: float = Field(..., ge=-90, le=90, description="위도")
    longitude: float = Field(..., ge=-180, le=180, description="경도")


class LocationModel(BaseModel):
    """위치 정보 모델"""
    id: str = Field(..., description="위치 ID")
    name: str = Field(..., description="위치명")
    latitude: float = Field(..., ge=-90, le=90, description="위도")
    longitude: float = Field(..., ge=-180, le=180, description="경도")
    address: Optional[str] = Field(None, description="주소")


class StopModel(BaseModel):
    """배송 정류소 모델"""
    id: str = Field(..., description="정류소 ID")
    name: str = Field(..., description="정류소명")
    latitude: float = Field(..., ge=-90, le=90, description="위도")
    longitude: float = Field(..., ge=-180, le=180, description="경도")
    demand: int = Field(..., ge=0, description="수량 (단위: kg)")
    address: Optional[str] = Field(None, description="주소")
    phone: Optional[str] = Field(None, description="연락처")
    time_window_start: Optional[int] = Field(None, description="배송 시간대 시작 (분 단위)")
    time_window_end: Optional[int] = Field(None, description="배송 시간대 종료 (분 단위)")


class VehicleModel(BaseModel):
    """차량 정보 모델"""
    id: str = Field(..., description="차량 ID")
    name: str = Field(..., description="차량명")
    vehicle_type: str = Field(..., description="차량 타입 (small/medium/large)")
    capacity: int = Field(..., ge=0, description="적재량 (단위: kg)")
    fuel_consumption: float = Field(..., gt=0, description="연비 (km/L)")
    fuel_cost_per_liter: float = Field(..., gt=0, description="리터당 연료비")
    cost_per_hour: float = Field(default=50000, gt=0, description="시간당 비용")
    available: bool = Field(default=True, description="사용 가능 여부")


class DistanceMatrixRequest(BaseModel):
    """거리 행렬 계산 요청"""
    origins: List[CoordinateModel] = Field(..., description="출발지 좌표 목록")
    destinations: List[CoordinateModel] = Field(..., description="목적지 좌표 목록")
    mode: str = Field(default="driving", description="이동 수단 (driving/walking/bicycling/transit)")


class DistanceAndDurationRequest(BaseModel):
    """거리 및 소요시간 요청"""
    origin: CoordinateModel = Field(..., description="출발지 좌표")
    destination: CoordinateModel = Field(..., description="목적지 좌표")
    mode: str = Field(default="driving", description="이동 수단")


class OptimizationRequest(BaseModel):
    """경로 최적화 요청"""
    vehicles: List[VehicleModel] = Field(..., description="차량 목록")
    stops: List[StopModel] = Field(..., description="배송 정류소 목록")
    start_location: LocationModel = Field(..., description="출발지 (창고)")
    end_location: Optional[LocationModel] = Field(None, description="도착지 (기본값: 출발지와 동일)")
    time_limit_seconds: int = Field(default=30, ge=1, le=600, description="최적화 시간 제한 (초)")
    use_cache: bool = Field(default=True, description="캐시 사용 여부")


class RouteStopResponse(BaseModel):
    """경로 상의 정류소 정보"""
    stop_id: str
    stop_name: str
    arrival_time: int
    departure_time: int
    demand: int
    cumulative_distance: float  # km
    cumulative_fuel_consumption: float  # L
    cumulative_cost: float  # 원


class OptimizedRouteResponse(BaseModel):
    """최적화된 경로 정보"""
    vehicle_id: str
    vehicle_name: str
    stops: List[RouteStopResponse]
    total_distance: float  # km
    total_fuel_consumption: float  # L
    total_cost: float  # 원
    total_demand: int
    utilization_rate: float  # %


class OptimizationResponse(BaseModel):
    """경로 최적화 응답"""
    success: bool
    message: str
    routes: Optional[List[OptimizedRouteResponse]] = None
    total_distance: Optional[float] = None
    total_fuel_consumption: Optional[float] = None
    total_cost: Optional[float] = None
    optimization_time_ms: int


class DistanceMatrixResponse(BaseModel):
    """거리 행렬 응답"""
    matrix: List[List[int]]  # 거리 (미터 단위)
    rows: int
    columns: int


class DistanceAndDurationResponse(BaseModel):
    """거리 및 소요시간 응답"""
    distance: int  # 미터 단위
    duration: int  # 초 단위
    distance_km: float
    duration_minutes: float


class HealthCheckResponse(BaseModel):
    """헬스 체크 응답"""
    status: str
    app_name: str
    version: str
    timestamp: str
