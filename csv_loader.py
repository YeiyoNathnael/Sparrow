"""
CSV data loader for bus clustering system.
Loads and merges student, school, association, and assembly point data.
"""
import csv
from typing import List, Dict, Tuple
from src.utils.data_structures import Student, AssemblyPoint


class CSVDataLoader:
    """
    Custom CSV data loader for clustering pipeline.
    """
    
    def __init__(self, 
                 students_csv: str,
                 schools_csv: str,
                 associations_csv: str,
                 assembly_csv: str):
        """
        Initialize loader with CSV file paths.
        
        Args:
            students_csv: Path to students CSV (student_id, lat, lon, ...)
            schools_csv: Path to schools CSV (school_id, latitude, longitude, ...)
            associations_csv: Path to student-school associations (student_id, school_id)
            assembly_csv: Path to assembly points CSV (stop_id, lat, lon, ...)
        """
        self.students_csv = students_csv
        self.schools_csv = schools_csv
        self.associations_csv = associations_csv
        self.assembly_csv = assembly_csv
        
        self.schools_dict = {}
        self.associations_dict = {}
    
    def load_schools(self) -> Dict[str, Tuple[float, float, str]]:
        """
        Load schools into dictionary.
        
        Returns:
            Dictionary: {school_id: (latitude, longitude, school_name)}
        """
        schools = {}
        
        with open(self.schools_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                school_id = row['school_id']
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                name = row['school_name']
                schools[school_id] = (lat, lon, name)
        
        print(f"✓ Loaded {len(schools)} schools from {self.schools_csv}")
        return schools
    
    def load_associations(self) -> Dict[str, str]:
        """
        Load student-school associations into dictionary.
        
        Returns:
            Dictionary: {student_id: school_id}
        """
        associations = {}
        
        with open(self.associations_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                student_id = row['student_id']
                school_id = row['school_id']
                associations[student_id] = school_id
        
        print(f"✓ Loaded {len(associations)} student-school associations from {self.associations_csv}")
        return associations
    
    def load_students(self) -> List[Student]:
        """
        Load students and merge with school associations.
        
        Returns:
            List of Student objects
        """
        # First load schools and associations
        self.schools_dict = self.load_schools()
        self.associations_dict = self.load_associations()
        
        students = []
        skipped_count = 0
        
        with open(self.students_csv, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                student_id = row['student_id']
                home_lat = float(row['lat'])
                home_lon = float(row['lon'])
                
                # Check if student has school association
                if student_id not in self.associations_dict:
                    print(f"⚠ Warning: Student {student_id} has no school association, skipping...")
                    skipped_count += 1
                    continue
                
                school_id = self.associations_dict[student_id]
                
                # Check if school exists
                if school_id not in self.schools_dict:
                    print(f"⚠ Warning: School {school_id} not found for student {student_id}, skipping...")
                    skipped_count += 1
                    continue
                
                school_lat, school_lon, school_name = self.schools_dict[school_id]
                
                # Create Student object
                student = Student(
                    student_id=student_id,
                    home_location=(home_lat, home_lon),
                    school_id=f"school_{school_id}",
                    school_location=(school_lat, school_lon)
                )
                students.append(student)
        
        print(f"✓ Loaded {len(students)} students from {self.students_csv}")
        if skipped_count > 0:
            print(f"  ({skipped_count} students skipped due to missing data)")
        
        return students
    
    def load_assembly_points(self) -> List[AssemblyPoint]:
        """
        Load assembly points from CSV.
        Ignores 'assigned_students' column.
        
        Returns:
            List of AssemblyPoint objects
        """
        assembly_points = []
        
        with open(self.assembly_csv, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                assembly_id = f"stop_{row['stop_id']}"
                lat = float(row['lat'])
                lon = float(row['lon'])
                
                assembly = AssemblyPoint(
                    assembly_id=assembly_id,
                    location=(lat, lon)
                )
                assembly_points.append(assembly)
        
        print(f"✓ Loaded {len(assembly_points)} assembly points from {self.assembly_csv}")
        return assembly_points
    
    def load_all(self) -> Tuple[List[Student], List[AssemblyPoint]]:
        """
        Load all data (students + assembly points).
        
        Returns:
            Tuple of (students, assembly_points)
        """
        print("\n" + "="*80)
        print("LOADING DATA FROM CSV FILES")
        print("="*80 + "\n")
        
        students = self.load_students()
        assembly_points = self.load_assembly_points()
        
        # Print summary
        unique_schools = set(s.school_id for s in students)
        
        print("\n" + "="*80)
        print("DATA LOADING SUMMARY")
        print("="*80)
        print(f"  Total Students: {len(students)}")
        print(f"  Assembly Points: {len(assembly_points)}")
        print(f"  Unique Schools: {len(unique_schools)}")
        print(f"  Schools: {sorted(unique_schools)[:5]}{'...' if len(unique_schools) > 5 else ''}")
        print("="*80 + "\n")
        
        return students, assembly_points
