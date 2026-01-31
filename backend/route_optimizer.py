"""
Route optimization logic for generating optimized bus routes with road snapping.
"""

import math
from typing import List, Dict, Tuple
from datetime import datetime
import requests
import json


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def get_route_polyline(start_point: Tuple[float, float], 
                       waypoints: List[Tuple[float, float]], 
                       end_point: Tuple[float, float],
                       use_osm_router: bool = False) -> Dict:
    """
    Get route polyline using OpenStreetMap Routing or return direct coords.
    If OSM is unavailable, returns straight line polyline.
    """
    coordinates = [start_point] + waypoints + [end_point]
    
    if use_osm_router:
        try:
            # Try using OSRM (Open Source Routing Machine) for real road routing
            # This is a public demo server - for production use your own instance
            coords_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
            url = f"https://router.project-osrm.org/route/v1/driving/{coords_str}"
            params = {
                "overview": "full",
                "geometries": "geojson",
                "steps": "false"
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("routes"):
                    route = data["routes"][0]
                    geometry = route.get("geometry", {})
                    if geometry.get("coordinates"):
                        # Convert from GeoJSON [lon, lat] to [[lat, lon], ...]
                        polyline = [[coord[1], coord[0]] for coord in geometry["coordinates"]]
                        distance = route.get("distance", 0) / 1000  # km
                        duration = route.get("duration", 0) / 60  # minutes
                        return {
                            "polyline": polyline,
                            "distance_km": distance,
                            "duration_minutes": duration,
                            "source": "osrm"
                        }
        except Exception as e:
            print(f"OSRM routing failed: {e}, falling back to direct route")
    
    # Fallback: return straight line coordinates
    distance = sum(
        haversine_distance(coordinates[i][0], coordinates[i][1], 
                          coordinates[i+1][0], coordinates[i+1][1])
        for i in range(len(coordinates) - 1)
    )
    
    # Estimate duration based on average speed of 30 km/h
    duration = (distance / 30) * 60
    
    return {
        "polyline": coordinates,
        "distance_km": distance,
        "duration_minutes": duration,
        "source": "direct"
    }


def cluster_students_by_zone(students: List[Dict], num_clusters: int = None) -> Dict[int, List[Dict]]:
    """
    Cluster students by geographical proximity.
    Uses a simple grid-based clustering approach.
    """
    if not students:
        return {}
    
    # Determine number of clusters dynamically if not specified
    if num_clusters is None:
        num_clusters = max(1, len(students) // 50)  # ~50 students per route
    
    # Use zone_name if available, otherwise use geographic clustering
    clusters = {}
    for student in students:
        zone = student.get("zone_name", "Unknown")
        if zone not in clusters:
            clusters[zone] = []
        clusters[zone].append(student)
    
    return clusters


def optimize_route_stops(school_point: Tuple[float, float],
                         student_points: List[Tuple[float, float]],
                         assembly_points: List[Tuple[float, float]],
                         peak_hours: bool = True) -> Dict:
    """
    Optimize pickup order using nearest neighbor algorithm.
    
    Peak hours consideration:
    - Morning: Students → School → Assembly points
    - Peak demand: Multiple small routes or express routes
    """
    
    if not student_points:
        return {
            "route_type": "empty",
            "stops": [],
            "school_point": school_point,
            "assembly_points": assembly_points,
            "optimization_score": 0
        }
    
    # Determine route type based on peak hours
    route_type = "peak_express" if peak_hours else "standard"
    
    # Use nearest neighbor to order pickups
    remaining = list(student_points)
    ordered_stops = []
    current = assembly_points[0] if assembly_points else school_point
    
    while remaining:
        # Find nearest point
        nearest_idx = min(
            range(len(remaining)),
            key=lambda i: haversine_distance(
                current[0], current[1],
                remaining[i][0], remaining[i][1]
            )
        )
        nearest = remaining.pop(nearest_idx)
        ordered_stops.append(nearest)
        current = nearest
    
    # Calculate route quality score (0-100)
    total_distance = sum(
        haversine_distance(
            ordered_stops[i][0], ordered_stops[i][1],
            ordered_stops[i+1][0], ordered_stops[i+1][1]
        )
        for i in range(len(ordered_stops) - 1)
    )
    # Score based on distance: closer routes get better scores
    optimization_score = max(0, 100 - (total_distance * 5))
    
    return {
        "route_type": route_type,
        "stops": ordered_stops,
        "school_point": school_point,
        "assembly_points": assembly_points,
        "total_distance_km": total_distance,
        "optimization_score": optimization_score
    }


def generate_optimized_routes(schools: List[Dict],
                            students: List[Dict],
                            assembly_points: List[Dict],
                            peak_hours: bool = True,
                            bus_capacity: int = 50,
                            use_road_snapping: bool = True) -> List[Dict]:
    """
    Generate optimized bus routes from schools to assembly points.
    
    Args:
        schools: List of school data with lat/lon
        students: List of student data with lat/lon and school_id
        assembly_points: List of assembly point data
        peak_hours: Whether to optimize for peak hours
        bus_capacity: Maximum students per bus
        use_road_snapping: Whether to use OSRM for road-based routing
    
    Returns:
        List of optimized routes with polylines
    """
    
    routes = []
    route_id = 1
    
    # Group students by school
    students_by_school = {}
    for student in students:
        school_id = student.get("school_id")
        if school_id not in students_by_school:
            students_by_school[school_id] = []
        students_by_school[school_id].append(student)
    
    print(f"DEBUG route_optimizer: Students by school - {len(students_by_school)} school groups")
    for school_id, student_list in students_by_school.items():
        print(f"  School {school_id}: {len(student_list)} students")
    
    # Generate routes for each school
    for school in schools:
        school_id = school["id"]
        school_coords = (school["latitude"], school["longitude"])
        school_students = students_by_school.get(school_id, [])
        
        print(f"DEBUG: Processing school {school_id} ({school['name']}), has {len(school_students)} students")
        
        if not school_students:
            continue
        
        # Split large groups into multiple routes
        for i in range(0, len(school_students), bus_capacity):
            batch = school_students[i:i + bus_capacity]
            student_coords = [(s["lat"], s["lon"]) for s in batch]
            assembly_coords = [(ap["lat"], ap["lon"]) for ap in assembly_points]
            
            # Optimize this route's stops
            optimization_data = optimize_route_stops(
                school_coords,
                student_coords,
                assembly_coords,
                peak_hours=peak_hours
            )
            
            # Get road-snapped polyline
            polyline_data = get_route_polyline(
                assembly_coords[0] if assembly_coords else school_coords,
                optimization_data["stops"][:10],  # Limit intermediate stops
                school_coords,
                use_osm_router=use_road_snapping
            )
            
            # Create route object
            route = {
                "id": f"route_{school_id}_{route_id}",
                "route_number": route_id,
                "school_id": school_id,
                "school_name": school["name"],
                "school_lat": school["latitude"],
                "school_lon": school["longitude"],
                "student_count": len(batch),
                "stop_count": len(optimization_data["stops"]),
                "assembly_point_count": len(assembly_coords),
                "polyline": polyline_data["polyline"],
                "distance_km": polyline_data["distance_km"],
                "duration_minutes": polyline_data["duration_minutes"],
                "optimization_score": optimization_data["optimization_score"],
                "route_type": optimization_data["route_type"],
                "peak_hours": peak_hours,
                "capacity": bus_capacity,
                "students": batch,
                "stops": optimization_data["stops"],
                "assembly_points": assembly_coords,
                "start_time": "06:30" if peak_hours else "07:30",
                "status": "scheduled"
            }
            
            routes.append(route)
            route_id += 1
    
    return routes
