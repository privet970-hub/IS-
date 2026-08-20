"""Route Optimization Service using Google OR-Tools"""
import time
from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from app.models.vehicle import Vehicle
from app.models.location import Stop, Location
from app.models.optimization import OptimizedRoute, RouteStop, OptimizationResponse


class RouteOptimizerService:
    """Service for route optimization using OR-Tools"""
    
    def __init__(self):
        self.routing = None
        self.manager = None
        self.solution = None
        
    def calculate_distance_matrix(self, locations: List[Location]) -> List[List[int]]:
        """
        Calculate distance matrix between all locations.
        In production, integrate with Google Maps API or similar.
        
        For now, using simplified Haversine formula for demonstration.
        """
        import math
        
        def haversine(lat1, lon1, lat2, lon2):
            """Calculate distance in meters between two coordinates"""
            R = 6371000  # Earth radius in meters
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            
            a = (math.sin(delta_phi / 2) ** 2 +
                 math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            return int(R * c)  # Return in meters
        
        num_locations = len(locations)
        matrix = [[0] * num_locations for _ in range(num_locations)]
        
        for i in range(num_locations):
            for j in range(num_locations):
                if i != j:
                    distance = haversine(
                        locations[i].latitude, locations[i].longitude,
                        locations[j].latitude, locations[j].longitude
                    )
                    matrix[i][j] = distance
        
        return matrix
    
    def optimize(
        self,
        vehicles: List[Vehicle],
        stops: List[Stop],
        start_location: Location,
        end_location: Location = None,
        time_limit_seconds: int = 30,
    ) -> OptimizationResponse:
        """
        Optimize routes for vehicles and stops using OR-Tools.
        
        Args:
            vehicles: List of available vehicles
            stops: List of stops to visit
            start_location: Depot starting location
            end_location: Depot ending location (if different)
            time_limit_seconds: Time limit for optimization
            
        Returns:
            OptimizationResponse with optimized routes
        """
        start_time = time.time()
        
        try:
            if end_location is None:
                end_location = start_location
            
            # Prepare locations list: [depot, ...stops, ...depot]
            all_locations = [start_location] + stops + [end_location]
            
            # Calculate distance matrix
            distance_matrix = self.calculate_distance_matrix(all_locations)
            
            # Create routing index manager
            self.manager = pywrapcp.RoutingIndexManager(
                len(all_locations),
                len(vehicles),
                0,  # Start from depot (index 0)
                len(all_locations) - 1 if start_location.id != end_location.id else 0  # End at depot
            )
            
            # Create routing model
            self.routing = pywrapcp.RoutingModel(self.manager)
            
            # Define distance callback
            def distance_callback(from_index, to_index):
                from_node = self.manager.IndexToNode(from_index)
                to_node = self.manager.IndexToNode(to_index)
                return distance_matrix[from_node][to_node]
            
            transit_callback_index = self.routing.RegisterTransitCallback(distance_callback)
            self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
            
            # Add capacity constraint
            def demand_callback(from_index):
                from_node = self.manager.IndexToNode(from_index)
                if from_node == 0 or from_node == len(all_locations) - 1:
                    return 0
                return int(stops[from_node - 1].demand)
            
            demand_callback_index = self.routing.RegisterUnaryTransitCallback(demand_callback)
            self.routing.AddDimensionWithSlackStartEndConnectorCallbacks(
                demand_callback_index,
                0,  # Slack
                [int(v.capacity) for v in vehicles],  # Vehicle capacities
                True,  # Start cumul to zero
                "Capacity"
            )
            
            # Set search parameters
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            )
            search_parameters.time_limit.seconds = int(time_limit_seconds)
            
            # Solve
            self.solution = self.routing.SolveFromAssignmentWithParameters(
                self.routing.ReadAssignmentFromRoutes([[]], True),
                search_parameters
            )
            
            # Extract optimized routes
            optimized_routes = self._extract_routes(all_locations, vehicles, stops)
            
            optimization_time_ms = int((time.time() - start_time) * 1000)
            
            return OptimizationResponse(
                success=True,
                message="Route optimization completed successfully",
                routes=optimized_routes,
                total_distance=sum(r.total_distance for r in optimized_routes),
                total_fuel_consumption=sum(r.total_fuel_consumption for r in optimized_routes),
                total_cost=sum(r.total_cost for r in optimized_routes),
                optimization_time_ms=optimization_time_ms,
            )
            
        except Exception as e:
            optimization_time_ms = int((time.time() - start_time) * 1000)
            return OptimizationResponse(
                success=False,
                message=f"Optimization failed: {str(e)}",
                optimization_time_ms=optimization_time_ms,
            )
    
    def _extract_routes(
        self,
        all_locations: List[Location],
        vehicles: List[Vehicle],
        stops: List[Stop],
    ) -> List[OptimizedRoute]:
        """
        Extract optimized routes from OR-Tools solution.
        """
        optimized_routes = []
        
        for vehicle_id in range(len(vehicles)):
            vehicle = vehicles[vehicle_id]
            route_indices = self.routing.GetRoute(vehicle_id)
            route_stops = []
            
            cumulative_distance = 0
            cumulative_demand = 0
            cumulative_fuel = 0
            cumulative_cost = 0
            
            index = route_indices.Start()
            
            while not route_indices.IsEnd(index):
                node_index = self.manager.IndexToNode(index)
                
                # Skip depot nodes at start and end
                if 0 < node_index < len(all_locations) - 1:
                    stop = stops[node_index - 1]
                    next_index = route_indices.Next(index)
                    next_node = self.manager.IndexToNode(next_index)
                    
                    distance = self.routing.GetArcCostForVehicle(index, next_index, vehicle_id)
                    cumulative_distance += distance
                    
                    # Calculate fuel consumption
                    distance_km = distance / 1000
                    fuel_used = (distance_km / 100) * vehicle.fuel_consumption
                    cumulative_fuel += fuel_used
                    cumulative_cost += fuel_used * vehicle.fuel_cost_per_liter
                    
                    cumulative_demand += stop.demand
                    
                    route_stops.append(
                        RouteStop(
                            stop_id=stop.id,
                            stop_name=stop.name,
                            arrival_time=0,  # TODO: Calculate from time windows
                            departure_time=0,
                            demand=stop.demand,
                            cumulative_distance=cumulative_distance / 1000,  # Convert to km
                            cumulative_fuel_consumption=cumulative_fuel,
                            cumulative_cost=cumulative_cost,
                        )
                    )
                
                index = route_indices.Next(index)
            
            if route_stops:  # Only add route if it has stops
                utilization = (cumulative_demand / vehicle.capacity * 100) if vehicle.capacity > 0 else 0
                
                optimized_routes.append(
                    OptimizedRoute(
                        vehicle_id=vehicle.id,
                        vehicle_name=vehicle.name,
                        stops=route_stops,
                        total_distance=cumulative_distance / 1000,  # Convert to km
                        total_fuel_consumption=cumulative_fuel,
                        total_cost=cumulative_cost,
                        total_demand=cumulative_demand,
                        utilization_rate=min(utilization, 100),
                    )
                )
        
        return optimized_routes
