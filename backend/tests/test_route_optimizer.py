"""Tests for Route Optimizer Service"""
import pytest
from app.services.route_optimizer import RouteOptimizerService
from app.models.vehicle import Vehicle, VehicleType
from app.models.location import Stop, Location


@pytest.fixture
def optimizer():
    """Create optimizer instance"""
    return RouteOptimizerService()


@pytest.fixture
def sample_vehicles():
    """Create sample vehicles"""
    return [
        Vehicle(
            id="v_001",
            name="Truck #1",
            vehicle_type=VehicleType.LARGE,
            capacity=20000,
            fuel_consumption=8.5,
            fuel_cost_per_liter=1500,
            start_location_id="depot",
        ),
        Vehicle(
            id="v_002",
            name="Truck #2",
            vehicle_type=VehicleType.MEDIUM,
            capacity=10000,
            fuel_consumption=6.5,
            fuel_cost_per_liter=1500,
            start_location_id="depot",
        ),
    ]


@pytest.fixture
def sample_stops():
    """Create sample delivery stops"""
    return [
        Stop(
            id="stop_001",
            name="Customer A",
            latitude=37.4979,
            longitude=127.0276,
            demand=5000,
        ),
        Stop(
            id="stop_002",
            name="Customer B",
            latitude=37.5665,
            longitude=126.9780,
            demand=3000,
        ),
        Stop(
            id="stop_003",
            name="Customer C",
            latitude=37.4419,
            longitude=126.7998,
            demand=4500,
        ),
    ]


@pytest.fixture
def sample_depot():
    """Create sample depot"""
    return Location(
        id="depot",
        name="Seoul Distribution Center",
        latitude=37.5665,
        longitude=126.9780,
    )


def test_optimize_routes(optimizer, sample_vehicles, sample_stops, sample_depot):
    """Test basic route optimization"""
    response = optimizer.optimize(
        vehicles=sample_vehicles,
        stops=sample_stops,
        start_location=sample_depot,
        time_limit_seconds=10,
    )
    
    assert response.success
    assert len(response.routes) > 0
    assert response.total_distance > 0
    assert response.total_fuel_consumption > 0
    assert response.total_cost > 0
