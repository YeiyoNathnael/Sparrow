"""
Distance computation utilities for geospatial coordinates.
"""
import torch
import numpy as np


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Compute Haversine distance between two points.
    
    Args:
        lat1, lon1: Latitude and longitude of first point (degrees)
        lat2, lon2: Latitude and longitude of second point (degrees)
    
    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth radius in kilometers
    
    # Convert to radians
    lat1_rad = torch.deg2rad(lat1) if isinstance(lat1, torch.Tensor) else np.radians(lat1)
    lon1_rad = torch.deg2rad(lon1) if isinstance(lon1, torch.Tensor) else np.radians(lon1)
    lat2_rad = torch.deg2rad(lat2) if isinstance(lat2, torch.Tensor) else np.radians(lat2)
    lon2_rad = torch.deg2rad(lon2) if isinstance(lon2, torch.Tensor) else np.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = torch.sin(dlat / 2) ** 2 + torch.cos(lat1_rad) * torch.cos(lat2_rad) * torch.sin(dlon / 2) ** 2
    c = 2 * torch.asin(torch.sqrt(a))
    
    return R * c


def batch_haversine_distance(coords1, coords2):
    """
    Compute pairwise Haversine distances between two sets of coordinates.
    
    Args:
        coords1: Tensor of shape (N, 2) containing [lat, lon] for N points
        coords2: Tensor of shape (M, 2) containing [lat, lon] for M points
    
    Returns:
        Distance matrix of shape (N, M) in kilometers
    """
    # Ensure tensors
    if not isinstance(coords1, torch.Tensor):
        coords1 = torch.tensor(coords1, dtype=torch.float32)
    if not isinstance(coords2, torch.Tensor):
        coords2 = torch.tensor(coords2, dtype=torch.float32)
    
    # Extract coordinates
    lat1 = coords1[:, 0].unsqueeze(1)  # (N, 1)
    lon1 = coords1[:, 1].unsqueeze(1)  # (N, 1)
    lat2 = coords2[:, 0].unsqueeze(0)  # (1, M)
    lon2 = coords2[:, 1].unsqueeze(0)  # (1, M)
    
    return haversine_distance(lat1, lon1, lat2, lon2)


def combined_distance(home_coords1, school_coords1, home_coords2, school_coords2,
                     home_weight=0.6, school_weight=0.4):
    """
    Compute combined distance considering both home and school locations.
    
    Args:
        home_coords1: Home coordinates (N, 2) [lat, lon]
        school_coords1: School coordinates (N, 2) [lat, lon]
        home_coords2: Home coordinates (M, 2) [lat, lon]
        school_coords2: School coordinates (M, 2) [lat, lon]
        home_weight: Weight for home proximity (default: 0.6)
        school_weight: Weight for school proximity (default: 0.4)
    
    Returns:
        Combined distance matrix (N, M)
    """
    home_dist = batch_haversine_distance(home_coords1, home_coords2)
    school_dist = batch_haversine_distance(school_coords1, school_coords2)
    
    # Normalize distances to [0, 1] range for stable weighting
    home_dist_norm = home_dist / (home_dist.max() + 1e-6)
    school_dist_norm = school_dist / (school_dist.max() + 1e-6)
    
    combined = home_weight * home_dist_norm + school_weight * school_dist_norm
    
    # Scale back to approximate kilometers
    combined = combined * (home_dist.max() + school_dist.max()) / 2
    
    return combined


def compute_centroid(coords):
    """
    Compute the geographic centroid of a set of coordinates.
    
    Args:
        coords: Tensor or array of shape (N, 2) containing [lat, lon]
    
    Returns:
        Centroid coordinates [lat, lon]
    """
    if not isinstance(coords, torch.Tensor):
        coords = torch.tensor(coords, dtype=torch.float32)
    
    return coords.mean(dim=0)


def compute_school_dispersion(school_coords):
    """
    Compute dispersion (variance) of school locations.
    Lower values indicate schools are closer together.
    
    Args:
        school_coords: Tensor of shape (N, 2) containing [lat, lon] for N schools
    
    Returns:
        Dispersion score (lower is better for clustering)
    """
    if len(school_coords) <= 1:
        return 0.0
    
    if not isinstance(school_coords, torch.Tensor):
        school_coords = torch.tensor(school_coords, dtype=torch.float32)
    
    centroid = compute_centroid(school_coords)
    distances = batch_haversine_distance(school_coords, centroid.unsqueeze(0))
    
    return distances.var().item()
