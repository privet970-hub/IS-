# Backend Architecture

## Overview

The backend is built with FastAPI and uses Google OR-Tools for route optimization.

## Core Components

### 1. API Layer (FastAPI)
- RESTful endpoints for route optimization
- Request/Response validation using Pydantic
- Swagger/OpenAPI documentation
- CORS support for frontend integration

### 2. Service Layer
- **RouteOptimizerService**: Handles route optimization logic
  - Integrates with Google OR-Tools
  - Calculates distance matrices
  - Manages vehicle and stop constraints
  - Extracts optimized routes from solutions

### 3. Data Models
- **Vehicle**: Represents a delivery vehicle with capacity, fuel consumption, etc.
- **Stop**: Represents a delivery/pickup location
- **Location**: Base location model with coordinates
- **OptimizationRequest**: Input for optimization
- **OptimizationResponse**: Output with optimized routes

## Key Features

### Route Optimization
- Multiple vehicles support
- Capacity constraints (weight/volume)
- Time window constraints (TODO)
- Distance and cost calculation
- Fuel consumption estimation
- Vehicle utilization rate

### Distance Calculation
- Uses Haversine formula for great-circle distance
- TODO: Integrate with Google Maps API for actual road distances
- TODO: Consider traffic and road restrictions

## API Endpoints (TODO)

- `POST /api/v1/optimize`: Submit optimization request
- `GET /api/v1/routes/{route_id}`: Get optimized route details
- `POST /api/v1/routes/{route_id}/tracking`: Update route tracking

## Technology Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Optimization**: Google OR-Tools
- **Data Validation**: Pydantic
- **Testing**: pytest
- **Database**: PostgreSQL (planned)

## Future Enhancements

1. Real-world distance matrix from Google Maps API
2. Time window support for delivery schedules
3. Driver break time constraints
4. Multi-day route planning
5. Real-time tracking integration
6. Dynamic re-routing based on traffic
7. Driver skill/specialization constraints
8. Vehicle maintenance schedule
9. Fuel type and availability
10. Environmental impact calculation
