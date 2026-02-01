"""
FastAPI Backend for Bus Route Optimization System

Serves optimized routes and dashboard data to the frontend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from pathlib import Path
from contextlib import asynccontextmanager

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR
DB_PATH = BASE_DIR / "backend" / "nexus.db"
OPTIMIZED_ROUTES_PATH = DATA_DIR / "optimized_routes.json"
ROUTE_INPUT_PATH = DATA_DIR / "route_optimizer_input.json"


def init_db():
    """Initialize SQLite database with routes data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id TEXT PRIMARY KEY,
            route_number INTEGER,
            school_names TEXT,
            student_count INTEGER,
            distance_km REAL,
            duration_minutes INTEGER,
            polyline TEXT,
            optimization_score INTEGER,
            route_type TEXT,
            start_time TEXT,
            status TEXT,
            num_pickups INTEGER,
            num_dropoffs INTEGER,
            depot_lat REAL,
            depot_lon REAL,
            buses_needed INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schools (
            id TEXT PRIMARY KEY,
            name TEXT,
            lat REAL,
            lon REAL,
            zone_id INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            school_id TEXT,
            assembly_point TEXT,
            lat REAL,
            lon REAL
        )
    ''')
    
    conn.commit()
    
    # Load routes data
    load_routes_to_db(conn)
    load_schools_to_db(conn)
    load_students_to_db(conn)
    
    conn.close()


def load_routes_to_db(conn):
    """Load optimized routes into database."""
    cursor = conn.cursor()
    
    # Clear existing routes
    cursor.execute('DELETE FROM routes')
    
    # Load optimized routes
    if OPTIMIZED_ROUTES_PATH.exists():
        with open(OPTIMIZED_ROUTES_PATH) as f:
            optimized = json.load(f)
    else:
        optimized = {}
    
    # Load route input for school names
    if ROUTE_INPUT_PATH.exists():
        with open(ROUTE_INPUT_PATH) as f:
            route_input = json.load(f)
            routes_meta = {f"bus_{r['route_id']}": r for r in route_input.get('routes', [])}
    else:
        routes_meta = {}
    
    route_number = 1
    for bus_id, route_data in optimized.items():
        # Get metadata from route input
        meta = routes_meta.get(bus_id, {})
        
        # Extract school names from dropoff nodes
        dropoff_nodes = meta.get('dropoff_nodes', [])
        school_names = list(set(node.get('node_id', '') for node in dropoff_nodes))
        
        # Calculate duration (assume 25 km/h average speed in urban area)
        distance = route_data.get('distance_km', 0)
        duration = int(distance / 25 * 60)  # minutes
        
        # Optimization score based on efficiency
        student_count = meta.get('total_students', 0)
        optimization_score = min(95, 70 + int(student_count / 5))
        
        # Get buses needed (overcapacity zones may need multiple buses)
        buses_needed = meta.get('buses_needed', 1)
        
        # Determine route type
        route_type = 'peak_express' if student_count > 40 else 'standard'
        
        # Start time (stagger routes)
        hour = 6 + (route_number - 1) // 4
        minute = ((route_number - 1) % 4) * 15
        start_time = f"{hour:02d}:{minute:02d}"
        
        cursor.execute('''
            INSERT INTO routes (id, route_number, school_names, student_count, 
                distance_km, duration_minutes, polyline, optimization_score,
                route_type, start_time, status, num_pickups, num_dropoffs,
                depot_lat, depot_lon, buses_needed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bus_id,
            route_number,
            json.dumps(school_names),
            student_count,
            round(distance, 2),
            duration,
            json.dumps(route_data.get('stops', [])),
            optimization_score,
            route_type,
            start_time,
            'scheduled',
            route_data.get('num_pickups', 0),
            route_data.get('num_dropoffs', 0),
            route_data.get('depot', [0, 0])[0],
            route_data.get('depot', [0, 0])[1],
            buses_needed
        ))
        
        route_number += 1
    
    conn.commit()
    print(f"✓ Loaded {route_number - 1} routes into database")


def load_schools_to_db(conn):
    """Load schools from route input data."""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM schools')
    
    if ROUTE_INPUT_PATH.exists():
        with open(ROUTE_INPUT_PATH) as f:
            route_input = json.load(f)
        
        schools_seen = set()
        for route in route_input.get('routes', []):
            zone_id = route.get('route_id', 0)
            for node in route.get('dropoff_nodes', []):
                school_id = node.get('node_id', '')
                if school_id and school_id not in schools_seen:
                    schools_seen.add(school_id)
                    loc = node.get('location', {})
                    cursor.execute('''
                        INSERT INTO schools (id, name, lat, lon, zone_id)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        school_id,
                        school_id.replace('_', ' ').title(),
                        loc.get('lat', 0),
                        loc.get('lon', 0),
                        zone_id
                    ))
        
        conn.commit()
        print(f"✓ Loaded {len(schools_seen)} schools into database")


def load_students_to_db(conn):
    """Load students from route input data."""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students')
    
    if ROUTE_INPUT_PATH.exists():
        with open(ROUTE_INPUT_PATH) as f:
            route_input = json.load(f)
        
        student_count = 0
        for route in route_input.get('routes', []):
            for node in route.get('pickup_nodes', []):
                assembly_id = node.get('node_id', '')
                loc = node.get('location', {})
                for student_id in node.get('students', []):
                    cursor.execute('''
                        INSERT OR IGNORE INTO students (id, school_id, assembly_point, lat, lon)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        student_id,
                        '',
                        assembly_id,
                        loc.get('lat', 0),
                        loc.get('lon', 0)
                    ))
                    student_count += 1
        
        conn.commit()
        print(f"✓ Loaded {student_count} students into database")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    print("🚀 Initializing database...")
    init_db()
    print("✅ Backend ready!")
    yield


app = FastAPI(
    title="Bus Route Optimization API",
    description="API for optimized school bus routes",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "database": str(DB_PATH)}


@app.get("/api/routes")
async def get_routes(peak_hours: bool = False):
    """
    Get all optimized routes.
    
    Args:
        peak_hours: If true, filter for peak hour routes only
    """
    conn = get_db()
    cursor = conn.cursor()
    
    if peak_hours:
        cursor.execute('SELECT * FROM routes WHERE route_type = ?', ('peak_express',))
    else:
        cursor.execute('SELECT * FROM routes')
    
    rows = cursor.fetchall()
    conn.close()
    
    routes = []
    for row in rows:
        school_names = json.loads(row['school_names'])
        routes.append({
            "id": row['id'],
            "route_number": row['route_number'],
            "school_name": school_names[0] if school_names else "Unknown",
            "school_names": school_names,
            "student_count": row['student_count'],
            "distance_km": row['distance_km'],
            "duration_minutes": row['duration_minutes'],
            "polyline": json.loads(row['polyline']),
            "optimization_score": row['optimization_score'],
            "route_type": row['route_type'],
            "start_time": row['start_time'],
            "status": row['status'],
            "num_pickups": row['num_pickups'],
            "num_dropoffs": row['num_dropoffs'],
            "depot": [row['depot_lat'], row['depot_lon']],
            "buses_needed": row['buses_needed'] if 'buses_needed' in row.keys() else 1
        })
    
    return {"routes": routes}


@app.get("/api/routes/{route_id}")
async def get_route(route_id: str):
    """Get a single route by ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM routes WHERE id = ?', (route_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"error": "Route not found"}
    
    school_names = json.loads(row['school_names'])
    return {
        "id": row['id'],
        "route_number": row['route_number'],
        "school_name": school_names[0] if school_names else "Unknown",
        "school_names": school_names,
        "student_count": row['student_count'],
        "distance_km": row['distance_km'],
        "duration_minutes": row['duration_minutes'],
        "polyline": json.loads(row['polyline']),
        "optimization_score": row['optimization_score'],
        "route_type": row['route_type'],
        "start_time": row['start_time'],
        "status": row['status'],
        "num_pickups": row['num_pickups'],
        "num_dropoffs": row['num_dropoffs'],
        "depot": [row['depot_lat'], row['depot_lon']],
        "buses_needed": row['buses_needed'] if 'buses_needed' in row.keys() else 1
    }


@app.get("/api/schools")
async def get_schools():
    """Get all schools with zone information."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM schools')
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row['id'],
            "name": row['name'],
            "lat": row['lat'],
            "lon": row['lon'],
            "zone_id": row['zone_id']
        }
        for row in rows
    ]


@app.get("/api/students")
async def get_students():
    """Get all students."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row['id'],
            "school_id": row['school_id'],
            "assembly_point": row['assembly_point'],
            "lat": row['lat'],
            "lon": row['lon']
        }
        for row in rows
    ]


@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard summary metrics."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Count routes
    cursor.execute('SELECT COUNT(*) as count FROM routes')
    total_routes = cursor.fetchone()['count']
    
    # Count students
    cursor.execute('SELECT COUNT(*) as count FROM students')
    total_students = cursor.fetchone()['count']
    
    # Count schools
    cursor.execute('SELECT COUNT(*) as count FROM schools')
    total_schools = cursor.fetchone()['count']
    
    # Get unique zones
    cursor.execute('SELECT COUNT(DISTINCT zone_id) as count FROM schools')
    total_zones = cursor.fetchone()['count']
    
    # Average students per route
    cursor.execute('SELECT AVG(student_count) as avg FROM routes')
    avg_students = cursor.fetchone()['avg'] or 0
    
    # Total distance
    cursor.execute('SELECT SUM(distance_km) as total FROM routes')
    total_distance = cursor.fetchone()['total'] or 0
    
    conn.close()
    
    return {
        "total_routes": total_routes,
        "total_students": total_students,
        "total_schools": total_schools,
        "total_zones": total_zones,
        "avg_students_per_route": round(avg_students, 1),
        "total_distance_km": round(total_distance, 1)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
