from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

class School(Base):
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    student_count = Column(Integer, default=0)
    cluster_zone = Column(String, index=True)
    
    students = relationship("Student", back_populates="school")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(String, primary_key=True, index=True)
    lat = Column(Float)
    lon = Column(Float)
    school_id = Column(Integer, ForeignKey("schools.id"), index=True)
    zone_name = Column(String, index=True)
    housing_type = Column(String, default="Apartments")
    
    school = relationship("School", back_populates="students")

class AssemblyPoint(Base):
    __tablename__ = "assembly_points"
    
    stop_id = Column(Integer, primary_key=True, index=True)
    stop_name = Column(String, index=True)
    lat = Column(Float)
    lon = Column(Float)
    type = Column(String)
    assigned_students = Column(Integer, default=0)

class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    status = Column(String, default="pending")
    result_json = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
