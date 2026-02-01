"""
Data structures for bus pooling clustering.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import torch


@dataclass
class Student:
    """Represents a student with home and school locations."""
    student_id: str
    home_location: Tuple[float, float]  # (latitude, longitude)
    school_id: str
    school_location: Tuple[float, float]  # (latitude, longitude)
    
    def __repr__(self):
        return f"Student({self.student_id}, home={self.home_location}, school={self.school_id})"


@dataclass
class AssemblyPoint:
    """Represents a predefined assembly/pickup point."""
    assembly_id: str
    location: Tuple[float, float]  # (latitude, longitude)
    max_capacity: Optional[int] = None  # Optional capacity limit for the assembly point
    
    def __repr__(self):
        return f"AssemblyPoint({self.assembly_id}, location={self.location})"


@dataclass
class School:
    """Represents a school."""
    school_id: str
    location: Tuple[float, float]  # (latitude, longitude)
    name: Optional[str] = None
    
    def __repr__(self):
        return f"School({self.school_id}, location={self.location})"


@dataclass
class AssemblyPointCluster:
    """
    Represents an assembly point with its assigned students.
    """
    assembly_point: AssemblyPoint
    students: List[Student] = field(default_factory=list)
    
    @property
    def student_count(self) -> int:
        return len(self.students)
    
    @property
    def school_distribution(self) -> Dict[str, int]:
        """Get count of students per school."""
        distribution = {}
        for student in self.students:
            distribution[student.school_id] = distribution.get(student.school_id, 0) + 1
        return distribution
    
    @property
    def unique_schools(self) -> List[str]:
        """Get list of unique school IDs."""
        return list(set(s.school_id for s in self.students))
    
    @property
    def home_centroid(self) -> Tuple[float, float]:
        """Compute centroid of student home locations."""
        if not self.students:
            return self.assembly_point.location
        homes = torch.tensor([s.home_location for s in self.students])
        centroid = homes.mean(dim=0)
        return tuple(centroid.tolist())
    
    @property
    def school_centroid(self) -> Tuple[float, float]:
        """Compute centroid of school locations for students."""
        if not self.students:
            return (0.0, 0.0)
        schools = torch.tensor([s.school_location for s in self.students])
        centroid = schools.mean(dim=0)
        return tuple(centroid.tolist())
    
    def get_walking_distances(self) -> List[float]:
        """Compute walking distance from each student's home to assembly point."""
        from src.utils.distance import haversine_distance
        distances = []
        for student in self.students:
            dist = haversine_distance(
                torch.tensor(student.home_location[0]),
                torch.tensor(student.home_location[1]),
                torch.tensor(self.assembly_point.location[0]),
                torch.tensor(self.assembly_point.location[1])
            )
            distances.append(dist.item())
        return distances


@dataclass
class BusZone:
    """
    Represents a bus zone (cluster) containing multiple assembly points.
    """
    zone_id: int
    assembly_clusters: List[AssemblyPointCluster] = field(default_factory=list)
    capacity: int = 20  # Default bus capacity
    buses_needed: int = 1  # Number of buses required for this zone
    
    @property
    def total_students(self) -> int:
        return sum(cluster.student_count for cluster in self.assembly_clusters)
    
    @property
    def assembly_point_ids(self) -> List[str]:
        return [cluster.assembly_point.assembly_id for cluster in self.assembly_clusters]
    
    @property
    def school_ids(self) -> List[str]:
        """Get unique school IDs served by this zone."""
        schools = set()
        for cluster in self.assembly_clusters:
            schools.update(cluster.unique_schools)
        return list(schools)
    
    @property
    def school_distribution(self) -> Dict[str, int]:
        """Get total count of students per school across all assembly points."""
        distribution = {}
        for cluster in self.assembly_clusters:
            for school_id, count in cluster.school_distribution.items():
                distribution[school_id] = distribution.get(school_id, 0) + count
        return distribution
    
    @property
    def zone_centroid(self) -> Tuple[float, float]:
        """Compute centroid of all assembly point locations in this zone."""
        if not self.assembly_clusters:
            return (0.0, 0.0)
        locations = torch.tensor([c.assembly_point.location for c in self.assembly_clusters])
        centroid = locations.mean(dim=0)
        return tuple(centroid.tolist())
    
    @property
    def home_centroid(self) -> Tuple[float, float]:
        """Compute centroid of all student home locations."""
        all_homes = []
        for cluster in self.assembly_clusters:
            all_homes.extend([s.home_location for s in cluster.students])
        if not all_homes:
            return (0.0, 0.0)
        homes = torch.tensor(all_homes)
        centroid = homes.mean(dim=0)
        return tuple(centroid.tolist())
    
    @property
    def school_centroid(self) -> Tuple[float, float]:
        """Compute centroid of all school locations."""
        all_schools = []
        for cluster in self.assembly_clusters:
            all_schools.extend([s.school_location for s in cluster.students])
        if not all_schools:
            return (0.0, 0.0)
        schools = torch.tensor(all_schools)
        centroid = schools.mean(dim=0)
        return tuple(centroid.tolist())
    
    @property
    def capacity_utilization(self) -> float:
        """Get capacity utilization as a fraction (0.0 to 1.0)."""
        return self.total_students / self.capacity if self.capacity > 0 else 0.0
    
    def is_capacity_exceeded(self) -> bool:
        """Check if zone exceeds capacity."""
        return self.total_students > self.capacity
    
    def __repr__(self):
        return f"BusZone(id={self.zone_id}, students={self.total_students}/{self.capacity}, " \
               f"assemblies={len(self.assembly_clusters)}, schools={len(self.school_ids)})"


@dataclass
class ClusteringInput:
    """
    Input data structure for the clustering pipeline.
    """
    students: List[Student]
    assembly_points: List[AssemblyPoint]
    bus_capacity: int = 20
    max_schools_per_zone: int = 3
    school_proximity_threshold: float = 5.0  # km
    home_weight: float = 0.6
    school_weight: float = 0.4
    
    def to_tensors(self):
        """Convert to PyTorch tensors for computation."""
        student_homes = torch.tensor([s.home_location for s in self.students], dtype=torch.float32)
        student_schools = torch.tensor([s.school_location for s in self.students], dtype=torch.float32)
        assembly_locations = torch.tensor([a.location for a in self.assembly_points], dtype=torch.float32)
        
        return {
            'student_homes': student_homes,
            'student_schools': student_schools,
            'assembly_locations': assembly_locations,
            'student_ids': [s.student_id for s in self.students],
            'school_ids': [s.school_id for s in self.students],
            'assembly_ids': [a.assembly_id for a in self.assembly_points]
        }


@dataclass
class ClusteringOutput:
    """
    Output data structure from the clustering pipeline.
    """
    zones: List[BusZone]
    clustering_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format for JSON serialization."""
        return {
            'zones': [
                {
                    'zone_id': zone.zone_id,
                    'assembly_nodes': zone.assembly_point_ids,
                    'schools': zone.school_ids,
                    'student_count': zone.total_students,
                    'capacity': zone.capacity,
                    'capacity_utilization': zone.capacity_utilization,
                    'school_distribution': zone.school_distribution,
                    'zone_centroid': zone.zone_centroid,
                    'home_centroid': zone.home_centroid,
                    'school_centroid': zone.school_centroid,
                    'num_assembly_points': len(zone.assembly_clusters)
                }
                for zone in self.zones
            ],
            'summary': {
                'total_zones': len(self.zones),
                'total_students': sum(z.total_students for z in self.zones),
                'avg_students_per_zone': sum(z.total_students for z in self.zones) / len(self.zones) if self.zones else 0,
                'avg_capacity_utilization': sum(z.capacity_utilization for z in self.zones) / len(self.zones) if self.zones else 0,
                'zones_over_capacity': sum(1 for z in self.zones if z.is_capacity_exceeded())
            },
            'metrics': self.clustering_metrics
        }
    
    def __repr__(self):
        return f"ClusteringOutput(zones={len(self.zones)}, " \
               f"total_students={sum(z.total_students for z in self.zones)})"
