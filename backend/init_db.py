#!/usr/bin/env python3
"""
Database initialization script for RTA NEXUS backend.
Loads CSV data into SQLite database with proper relationships.
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from database import Base, DATABASE_URL, init_database
from models import School, Student, AssemblyPoint


def load_schools(session, csv_path):
    """Load schools from CSV file."""
    print(f"Loading schools from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    schools = []
    for _, row in df.iterrows():
        school = School(
            id=int(row['school_id']) if pd.notna(row.get('school_id')) else None,
            name=str(row['school_name']),
            latitude=float(row['latitude']) if pd.notna(row.get('latitude')) else 0.0,
            longitude=float(row['longitude']) if pd.notna(row.get('longitude')) else 0.0,
            student_count=int(row['student_count_est']) if pd.notna(row.get('student_count_est')) else 0,
            cluster_zone=str(row.get('cluster_zone', 'Unknown'))
        )
        schools.append(school)
    
    session.add_all(schools)
    session.commit()
    print(f"✓ Loaded {len(schools)} schools")
    return schools


def load_students(session, csv_path, schools_by_id):
    """Load students from CSV file."""
    print(f"Loading students from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Load associations from student_school_association.csv
    assoc_path = '/Users/akramjemal/Downloads/the bounty challenge/student_school_association.csv'
    print(f"Loading student-school associations from {assoc_path}...")
    assoc_df = pd.read_csv(assoc_path)
    assoc_dict = dict(zip(assoc_df['student_id'], assoc_df['school_id']))
    
    students = []
    for _, row in df.iterrows():
        student_id = str(row['student_id']) if pd.notna(row.get('student_id')) else None
        # Get school_id from association file
        school_id = assoc_dict.get(student_id, None)
        
        student = Student(
            id=student_id,
            lat=float(row['lat']) if pd.notna(row.get('lat')) else 0.0,
            lon=float(row['lon']) if pd.notna(row.get('lon')) else 0.0,
            school_id=school_id,
            zone_name=str(row.get('zone_name', 'Unknown')),
            housing_type=str(row.get('housing_type', 'villa'))
        )
        students.append(student)
    
    session.add_all(students)
    session.commit()
    print(f"✓ Loaded {len(students)} students")
    return students


def load_assembly_points(session, csv_path):
    """Load assembly/pickup points from CSV file."""
    print(f"Loading assembly points from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    points = []
    for _, row in df.iterrows():
        point = AssemblyPoint(
            stop_id=int(row.get('stop_id', 0)) if pd.notna(row.get('stop_id')) else 0,
            stop_name=str(row.get('stop_name', '')),
            lat=float(row['lat']) if pd.notna(row.get('lat')) else 0.0,
            lon=float(row['lon']) if pd.notna(row.get('lon')) else 0.0,
            type=str(row.get('type', 'pickup')),
            assigned_students=int(row.get('assigned_students', 0)) if pd.notna(row.get('assigned_students')) else 0
        )
        points.append(point)
    
    session.add_all(points)
    session.commit()
    print(f"✓ Loaded {len(points)} assembly points")
    return points


def main():
    """Main initialization function."""
    print("=" * 50)
    print("RTA NEXUS Database Initialization")
    print("=" * 50)
    
    # Create database and tables
    print("\nInitializing database...")
    init_database()
    print("✓ Database initialized")
    
    # Create session
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Define data directory
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # Load schools
        schools_csv = os.path.join(data_dir, 'barsha_schools_synthetic.csv')
        if os.path.exists(schools_csv):
            load_schools(session, schools_csv)
        else:
            print(f"⚠ Schools CSV not found: {schools_csv}")
        
        # Load assembly points
        assembly_csv = os.path.join(data_dir, 'assembly_points.csv')
        if os.path.exists(assembly_csv):
            load_assembly_points(session, assembly_csv)
        else:
            print(f"⚠ Assembly points CSV not found: {assembly_csv}")
        
        # Load students
        students_csv = os.path.join(data_dir, 'barsha_students_synthetic.csv')
        if os.path.exists(students_csv):
            load_students(session, students_csv, {})
        else:
            print(f"⚠ Students CSV not found: {students_csv}")
        
        print("\n" + "=" * 50)
        print("✓ Database initialization complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
