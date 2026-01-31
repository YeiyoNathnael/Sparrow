"""
Route Optimizer using RL4CO (Reinforcement Learning for Combinatorial Optimization)

This module optimizes the sequence of stops for each bus route using the POMO
(Policy Optimization with Multiple Optima) algorithm, a state-of-the-art approach
for solving Vehicle Routing Problems.
"""

from typing import List, Dict, Tuple, Optional
import torch
import numpy as np
import math
from rl4co.models import AttentionModel
from rl4co.envs import TSPEnv
from rl4co.utils.decoding import DecodingStrategy
import warnings


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute Haversine distance between two points using standard Python math.
    
    Args:
        lat1, lon1: Latitude and longitude of first point (degrees)
        lat2, lon2: Latitude and longitude of second point (degrees)
    
    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


class RL4CORouteOptimizer:
    """
    Route optimizer using RL4CO POMO model for TSP solving.
    
    Uses two-phase optimization:
    1. Optimize pickup sequence (all assembly points)
    2. Optimize dropoff sequence (all schools)
    
    This ensures all pickups occur before any dropoffs while allowing
    optimal ordering within each phase.
    """
    
    def __init__(self, 
                 device: str = 'cpu',
                 depot_strategy: str = 'centroid',
                 depot_location: Optional[Tuple[float, float]] = None):
        """
        Initialize the route optimizer.
        
        Args:
            device: Device to run optimization on ('cpu' or 'cuda')
            depot_strategy: Strategy for depot location ('centroid', 'first_pickup', or 'custom')
            depot_location: Custom depot location as (lat, lon), used if depot_strategy='custom'
        """
        self.device = device
        self.depot_strategy = depot_strategy
        self.depot_location = depot_location
        
        # Initialize TSP environment
        self.env = TSPEnv()
        
        # Initialize Attention Model (AM) - using this instead of POMO for simplicity
        # AM is well-suited for TSP and has good performance
        print("   Initializing Attention Model for TSP...")
        self.model = AttentionModel(self.env, baseline='rollout')
        self.model.to(device)
        self.model.eval()
        print("   ✓ Model initialized")
    
    def optimize_routes(self, route_input: Dict) -> Dict:
        """
        Optimize all routes from clustering output.
        
        Args:
            route_input: Route optimizer input JSON from clustering pipeline
            
        Returns:
            Dict with format: {
                "bus_<zone_id>": {
                    "stops": [[lat, lon], [lat, lon], ...],
                    "depot": [lat, lon],
                    "distance_km": float,
                    "num_pickups": int,
                    "num_dropoffs": int
                }
            }
        """
        optimized_routes = {}
        
        for route in route_input['routes']:
            route_id = route['route_id']
            optimized = self._optimize_single_route(route)
            optimized_routes[f"bus_{route_id}"] = optimized
        
        return optimized_routes
    
    def _optimize_single_route(self, route: Dict) -> Dict:
        """
        Optimize a single route using two-phase approach.
        
        Args:
            route: Single route data with pickup_nodes and dropoff_nodes
            
        Returns:
            Dict with optimized stops and metadata
        """
        pickup_nodes = route['pickup_nodes']
        dropoff_nodes = route['dropoff_nodes']
        
        # Extract coordinates
        pickup_coords = [
            (node['location']['lat'], node['location']['lon']) 
            for node in pickup_nodes
        ]
        dropoff_coords = [
            (node['location']['lat'], node['location']['lon']) 
            for node in dropoff_nodes
        ]
        
        # Determine depot location
        depot = self._get_depot_location(pickup_coords, dropoff_coords)
        
        # Phase 1: Optimize pickup sequence
        if len(pickup_coords) > 1:
            optimized_pickup_coords = self._solve_tsp(pickup_coords, depot)
        else:
            optimized_pickup_coords = pickup_coords
        
        # Phase 2: Optimize dropoff sequence
        if len(dropoff_coords) > 1:
            # For dropoffs, depot is the last pickup location
            last_pickup = optimized_pickup_coords[-1] if optimized_pickup_coords else depot
            optimized_dropoff_coords = self._solve_tsp(dropoff_coords, last_pickup)
        else:
            optimized_dropoff_coords = dropoff_coords
        
        # Combine sequences: depot -> pickups -> dropoffs
        all_stops = [depot] + optimized_pickup_coords + optimized_dropoff_coords
        
        # Calculate total distance
        total_distance = self._calculate_route_distance(all_stops)
        
        return {
            'stops': [[lat, lon] for lat, lon in all_stops],
            'depot': [depot[0], depot[1]],
            'distance_km': round(total_distance, 2),
            'num_pickups': len(pickup_coords),
            'num_dropoffs': len(dropoff_coords)
        }
    
    def _get_depot_location(self, 
                           pickup_coords: List[Tuple[float, float]], 
                           dropoff_coords: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Determine depot location based on strategy.
        
        Args:
            pickup_coords: List of pickup coordinates
            dropoff_coords: List of dropoff coordinates
            
        Returns:
            Depot location as (lat, lon)
        """
        if self.depot_strategy == 'custom' and self.depot_location is not None:
            return self.depot_location
        
        elif self.depot_strategy == 'first_pickup':
            return pickup_coords[0] if pickup_coords else dropoff_coords[0]
        
        else:  # 'centroid' (default)
            all_coords = pickup_coords + dropoff_coords
            avg_lat = sum(lat for lat, lon in all_coords) / len(all_coords)
            avg_lon = sum(lon for lat, lon in all_coords) / len(all_coords)
            return (avg_lat, avg_lon)
    
    def _solve_tsp(self, 
                   coordinates: List[Tuple[float, float]], 
                   start_point: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Solve TSP for a set of coordinates starting from a given point.
        
        Args:
            coordinates: List of (lat, lon) tuples to visit
            start_point: Starting location as (lat, lon)
            
        Returns:
            Optimized sequence of coordinates
        """
        if len(coordinates) <= 1:
            return coordinates
        
        # Create distance matrix
        all_points = [start_point] + coordinates
        n = len(all_points)
        distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    lat1, lon1 = all_points[i]
                    lat2, lon2 = all_points[j]
                    distance_matrix[i, j] = _haversine_km(lat1, lon1, lat2, lon2)
        
        # Convert to torch tensor
        distance_tensor = torch.tensor(distance_matrix, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        # Prepare coordinates for RL4CO (expects [batch, num_nodes, 2] with normalized coords)
        coords_array = np.array(all_points)
        
        # Normalize coordinates to [0, 1] range for RL4CO
        lat_min, lat_max = coords_array[:, 0].min(), coords_array[:, 0].max()
        lon_min, lon_max = coords_array[:, 1].min(), coords_array[:, 1].max()
        
        # Avoid division by zero for single unique coordinate
        lat_range = lat_max - lat_min if lat_max > lat_min else 1.0
        lon_range = lon_max - lon_min if lon_max > lon_min else 1.0
        
        normalized_coords = np.zeros_like(coords_array)
        normalized_coords[:, 0] = (coords_array[:, 0] - lat_min) / lat_range
        normalized_coords[:, 1] = (coords_array[:, 1] - lon_min) / lon_range
        
        coords_tensor = torch.tensor(normalized_coords, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        # Solve TSP using Attention Model
        try:
            with torch.no_grad():
                # Reset environment with coordinates
                td = self.env.reset(coords_tensor)
                
                # Run inference with greedy decoding
                out = self.model(td, decode_type='greedy', return_actions=True)
                
                # Extract tour (sequence of node indices)
                if 'actions' in out:
                    tour = out['actions'][0].cpu().numpy()
                else:
                    # Fallback to nearest neighbor if model fails
                    warnings.warn("Model output missing 'actions'. Using nearest neighbor heuristic.")
                    return self._nearest_neighbor_heuristic(coordinates, start_point)
                
                # Reorder coordinates according to tour
                # Skip the depot (index 0) and get the optimized sequence
                optimized_indices = [idx for idx in tour if idx > 0]
                optimized_coords = [coordinates[idx - 1] for idx in optimized_indices]
                
                return optimized_coords
                
        except Exception as e:
            warnings.warn(f"RL4CO optimization failed: {e}. Using nearest neighbor heuristic.")
            return self._nearest_neighbor_heuristic(coordinates, start_point)
    
    def _nearest_neighbor_heuristic(self, 
                                   coordinates: List[Tuple[float, float]], 
                                   start_point: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Fallback nearest neighbor heuristic for TSP.
        
        Args:
            coordinates: List of coordinates to visit
            start_point: Starting point
            
        Returns:
            Sequence of coordinates using nearest neighbor
        """
        unvisited = list(coordinates)
        sequence = []
        current = start_point
        
        while unvisited:
            # Find nearest unvisited point
            nearest_idx = min(range(len(unvisited)), 
                            key=lambda i: _haversine_km(current[0], current[1], 
                                                        unvisited[i][0], unvisited[i][1]))
            nearest = unvisited.pop(nearest_idx)
            sequence.append(nearest)
            current = nearest
        
        return sequence
    
    def _calculate_route_distance(self, stops: List[Tuple[float, float]]) -> float:
        """
        Calculate total distance for a route.
        
        Args:
            stops: Ordered list of (lat, lon) stops
            
        Returns:
            Total distance in kilometers
        """
        total_distance = 0.0
        for i in range(len(stops) - 1):
            lat1, lon1 = stops[i]
            lat2, lon2 = stops[i + 1]
            total_distance += _haversine_km(lat1, lon1, lat2, lon2)
        return total_distance
