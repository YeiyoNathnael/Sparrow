from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import json
import uuid
from database import get_db, init_database
from models import School, Student, AssemblyPoint, OptimizationRun
from pydantic import BaseModel
from route_optimizer import generate_optimized_routes

app = FastAPI(
    title="RTA Nexus Backend",
    description="Bus pooling optimization API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_database()
    print("✓ FastAPI backend started on port 8000")

class SchoolResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    student_count: int
    cluster_zone: str
    
    class Config:
        from_attributes = True

class StudentResponse(BaseModel):
    id: str
    lat: float
    lon: float
    school_id: int
    zone_name: str
    housing_type: str
    
    class Config:
        from_attributes = True

class AssemblyPointResponse(BaseModel):
    stop_id: int
    stop_name: str
    lat: float
    lon: float
    type: str
    assigned_students: int
    
    class Config:
        from_attributes = True

class OptimizeRequest(BaseModel):
    student_ids: list
    capacity: int = 50
    config: dict = {}

class OptimizationStatusResponse(BaseModel):
    id: str
    status: str
    result_json: str = None

@app.get("/")
async def root():
    return {
        "message": "RTA Nexus Backend",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/schools", response_model=list[SchoolResponse])
async def get_schools(db: Session = Depends(get_db)):
    schools = db.query(School).all()
    return schools

@app.get("/api/students", response_model=list[StudentResponse])
async def get_students(skip: int = 0, limit: int = 2000, db: Session = Depends(get_db)):
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@app.get("/api/assembly-points", response_model=list[AssemblyPointResponse])
async def get_assembly_points(db: Session = Depends(get_db)):
    points = db.query(AssemblyPoint).all()
    return points

@app.get("/api/routes")
async def get_optimized_routes(peak_hours: bool = True, db: Session = Depends(get_db)):
    """
    Generate optimized routes based on student-school associations.
    Uses road snapping for realistic route paths.
    """
    try:
        # Fetch all required data
        schools = db.query(School).all()
        students = db.query(Student).all()
        assembly_points = db.query(AssemblyPoint).all()
        
        print(f"DEBUG: Found {len(schools)} schools, {len(students)} students, {len(assembly_points)} assembly points")
        
        # Validate data
        if not schools:
            raise ValueError("No schools found in database")
        if not students:
            raise ValueError("No students found in database")
        if not assembly_points:
            raise ValueError("No assembly points found in database")
        
        # Convert to dicts for route optimizer
        schools_data = [
            {
                "id": s.id,
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "student_count": s.student_count,
                "cluster_zone": s.cluster_zone
            }
            for s in schools
        ]
        
        students_data = [
            {
                "id": s.id,
                "lat": s.lat,
                "lon": s.lon,
                "school_id": s.school_id,
                "zone_name": s.zone_name,
                "housing_type": s.housing_type
            }
            for s in students
        ]
        
        assembly_points_data = [
            {
                "id": ap.stop_id,
                "lat": ap.lat,
                "lon": ap.lon,
                "name": ap.stop_name,
                "type": ap.type,
                "assigned_students": ap.assigned_students
            }
            for ap in assembly_points
        ]
        
        print(f"DEBUG: Generated {len(schools_data)} school dicts, {len(students_data)} student dicts")
        
        # Generate optimized routes with road snapping
        routes = generate_optimized_routes(
            schools=schools_data,
            students=students_data,
            assembly_points=assembly_points_data,
            peak_hours=peak_hours,
            bus_capacity=50,
            use_road_snapping=True
        )
        
        print(f"DEBUG: Generated {len(routes)} routes")
        
        # Return simplified route info for frontend
        return {
            "total_routes": len(routes),
            "peak_hours": peak_hours,
            "routes": [
                {
                    "id": r["id"],
                    "route_number": r["route_number"],
                    "school_name": r["school_name"],
                    "student_count": r["student_count"],
                    "distance_km": round(r["distance_km"], 2),
                    "duration_minutes": round(r["duration_minutes"], 1),
                    "polyline": r["polyline"],
                    "optimization_score": round(r["optimization_score"], 1),
                    "route_type": r["route_type"],
                    "start_time": r["start_time"],
                    "status": r["status"]
                }
                for r in routes[:20]  # Limit to first 20 routes for initial display
            ]
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR generating routes: {e}")
        print(f"TRACEBACK: {error_trace}")
        return {
            "total_routes": 0,
            "peak_hours": peak_hours,
            "routes": [],
            "error": str(e),
            "error_trace": error_trace
        }

@app.get("/api/routes/{route_id}")
async def get_route_detail(route_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific route including all students and stops."""
    try:
        schools = db.query(School).all()
        students = db.query(Student).all()
        assembly_points = db.query(AssemblyPoint).all()
        
        # Convert to dicts
        schools_data = [
            {
                "id": s.id,
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "student_count": s.student_count,
                "cluster_zone": s.cluster_zone
            }
            for s in schools
        ]
        
        students_data = [
            {
                "id": s.id,
                "lat": s.lat,
                "lon": s.lon,
                "school_id": s.school_id,
                "zone_name": s.zone_name,
                "housing_type": s.housing_type
            }
            for s in students
        ]
        
        assembly_points_data = [
            {
                "id": ap.stop_id,
                "lat": ap.lat,
                "lon": ap.lon,
                "name": ap.stop_name,
                "type": ap.type,
                "assigned_students": ap.assigned_students
            }
            for ap in assembly_points
        ]
        
        # Generate all routes and find the one requested
        routes = generate_optimized_routes(
            schools=schools_data,
            students=students_data,
            assembly_points=assembly_points_data,
            peak_hours=True,
            bus_capacity=50,
            use_road_snapping=True
        )
        
        route = next((r for r in routes if r["id"] == route_id), None)
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return route
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def optimize_route_task(run_id: str, student_ids: list, db: Session):
    try:
        run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
        run.status = "processing"
        db.commit()
        
        import time
        time.sleep(5)
        
        students = db.query(Student).filter(Student.id.in_(student_ids)).all()
        
        result = {
            "run_id": run_id,
            "total_students": len(students),
            "estimated_distance": 42.5,
            "estimated_time": "1h 15m",
            "stops": [{"id": s.id, "lat": s.lat, "lon": s.lon} for s in students]
        }
        
        run.result_json = json.dumps(result)
        run.status = "completed"
        db.commit()
        
    except Exception as e:
        run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
        run.status = "failed"
        db.commit()
        print(f"Error in optimization task: {e}")

@app.post("/api/optimize", response_model=OptimizationStatusResponse)
async def optimize_route(request: OptimizeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    
    student_count = db.query(func.count(Student.id)).filter(Student.id.in_(request.student_ids)).scalar()
    if student_count == 0:
        raise HTTPException(status_code=404, detail="No valid students provided")
    
    run_id = str(uuid.uuid4())
    run = OptimizationRun(id=run_id, status="pending")
    db.add(run)
    db.commit()
    
    background_tasks.add_task(optimize_route_task, run_id, request.student_ids, db)
    
    return {"id": run_id, "status": "pending"}

@app.get("/api/status/{run_id}", response_model=OptimizationStatusResponse)
async def get_status(run_id: str, db: Session = Depends(get_db)):
    run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "id": run.id,
        "status": run.status,
        "result_json": run.result_json
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
