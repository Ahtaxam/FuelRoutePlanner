from math import radians, sin, cos, sqrt, atan2
from typing import List, Tuple, Dict, Set, Optional
from rtree import index
from collections import defaultdict
import math
from .load_data import FuelStation


def is_valid_coordinate(value: float) -> bool:
    """Check if coordinate value is valid"""
    return (value is not None and 
            isinstance(value, (int, float)) and 
            not math.isnan(value) and 
            not math.isinf(value))

def create_grid_index(stations: List[FuelStation], grid_size: float = 1.0) -> Dict[tuple, List[int]]:
    """
    Create a grid-based spatial index with validation
    """
    grid = defaultdict(list)
    for idx, station in enumerate(stations):
        # Validate coordinates
        if not (is_valid_coordinate(station.latitude) and is_valid_coordinate(station.longitude)):
            print(f"Warning: Skipping station with invalid coordinates: {station.name} ({station.latitude}, {station.longitude})")
            continue
            
        try:
            # Ensure coordinates are within valid ranges
            lat = max(-90, min(90, station.latitude))
            lon = max(-180, min(180, station.longitude))
            
            # Get grid cell coordinates
            cell_x = int(math.floor(lon / grid_size))
            cell_y = int(math.floor(lat / grid_size))
            
            # Add station index to cell
            grid[(cell_x, cell_y)].append(idx)
        except Exception as e:
            print(f"Warning: Error processing station {station.name}: {str(e)}")
            continue
            
    return grid

def get_nearby_cells(lon: float, lat: float, radius: float, grid_size: float) -> Set[tuple]:
    """Get all grid cells that could contain stations within radius"""
    try:
        # Validate inputs
        if not all(is_valid_coordinate(x) for x in [lon, lat, radius, grid_size]):
            return set()
            
        # Ensure coordinates are within valid ranges
        lat = max(-90, min(90, lat))
        lon = max(-180, min(180, lon))
        
        # Convert radius from miles to approximate degrees
        degree_radius = abs(radius / 69.0)
        
        # Calculate cell range
        min_x = int(math.floor((lon - degree_radius) / grid_size))
        max_x = int(math.ceil((lon + degree_radius) / grid_size))
        min_y = int(math.floor((lat - degree_radius) / grid_size))
        max_y = int(math.ceil((lat + degree_radius) / grid_size))
        
        # Return all cells in range
        return {(x, y) 
                for x in range(min_x, max_x + 1)
                for y in range(min_y, max_y + 1)}
    except Exception as e:
        print(f"Warning: Error getting nearby cells: {str(e)}")
        return set()

def validate_coordinates(coordinates: List[List[float]]) -> List[List[float]]:
    """Filter out invalid coordinates"""
    valid_coords = []
    for coord in coordinates:
        try:
            if (len(coord) >= 2 and 
                is_valid_coordinate(coord[0]) and 
                is_valid_coordinate(coord[1])):
                # Ensure coordinates are within valid ranges
                lon = max(-180, min(180, coord[0]))
                lat = max(-90, min(90, coord[1]))
                valid_coords.append([lon, lat])
        except Exception:
            continue
    return valid_coords


# This will try to find the fuel station nearest to each coordinate of the route
# I am using grid base search for optimization
def find_stations_along_route(coordinates: List[List[float]], 
                            stations: List[FuelStation],
                            max_deviation_miles: float = 5) -> List[FuelStation]:
    """
    Find stations near route using grid-based spatial partitioning with error handling
    """
    try:
        # Validate inputs
        if not coordinates or not stations or not is_valid_coordinate(max_deviation_miles):
            return []
            
        # Filter out invalid coordinates
        valid_coordinates = validate_coordinates(coordinates)
        if not valid_coordinates:
            print("Warning: No valid coordinates found")
            return []
            
        # Choose grid size based on max_deviation_miles
        grid_size = abs(max_deviation_miles / 69.0) * 2
        if not is_valid_coordinate(grid_size) or grid_size <= 0:
            print("Warning: Invalid grid size calculated")
            return []
            
        # Create grid index
        grid = create_grid_index(stations, grid_size)
        if not grid:
            print("Warning: No valid stations in grid")
            return []
            
        # Keep track of found stations
        found_station_indices = set()
        
        # Process each coordinate
        for coord in valid_coordinates:
            try:
                # Get relevant grid cells
                nearby_cells = get_nearby_cells(
                    coord[0],  # longitude
                    coord[1],  # latitude
                    max_deviation_miles,
                    grid_size
                )
                
                # Check stations in nearby cells
                for cell in nearby_cells:
                    if cell in grid:
                        for station_idx in grid[cell]:
                            if station_idx not in found_station_indices:
                                station = stations[station_idx]
                                try:
                                    distance = calculate_distance(
                                        station.latitude,
                                        station.longitude,
                                        coord[1],  # latitude
                                        coord[0]   # longitude
                                    )
                                    if (is_valid_coordinate(distance) and 
                                        distance <= max_deviation_miles):
                                        found_station_indices.add(station_idx)
                                except Exception as e:
                                    print(f"Warning: Error calculating distance: {str(e)}")
                                    continue
            except Exception as e:
                print(f"Warning: Error processing coordinate {coord}: {str(e)}")
                continue
        
        # Convert indices to stations
        return [stations[idx] for idx in found_station_indices]
        
    except Exception as e:
        print(f"Error in find_stations_along_route: {str(e)}")
        return []

def batch_process_coordinates(coordinates: List[List[float]], 
                            stations: List[FuelStation],
                            max_deviation_miles: float = 5,
                            batch_size: int = 100) -> List[FuelStation]:
    """
    Process coordinates in batches with error handling
    """
    try:
        if not coordinates or not stations:
            return []
            
        all_station_indices = set()
        
        # Process coordinates in batches
        for i in range(0, len(coordinates), batch_size):
            try:
                batch = coordinates[i:i + batch_size]
                batch_stations = find_stations_along_route(batch, stations, max_deviation_miles)
                
                # Add to overall results
                for station in batch_stations:
                    try:
                        idx = stations.index(station)
                        all_station_indices.add(idx)
                    except ValueError:
                        continue
                        
            except Exception as e:
                print(f"Warning: Error processing batch {i}: {str(e)}")
                continue
        
        # Convert indices to stations
        return [stations[idx] for idx in all_station_indices]
        
    except Exception as e:
        print(f"Error in batch_process_coordinates: {str(e)}")
        return []

def find_optimal_fuel_stops(route_stations: List[FuelStation], total_distance: float, 
                           max_range: float = 500, mpg: float = 10) -> List[FuelStation]:
    """Find optimal fuel stops based on price and distance"""
    current_range = max_range
    optimal_stops = []
    last_stop_index = 0
    distance_covered = 0
    
    while distance_covered < total_distance:
        best_station = None
        best_score = float('inf')
        
        # Look at stations within current range
        for i, station in enumerate(route_stations[last_stop_index:], last_stop_index):
            if i == last_stop_index:
                continue
                
            distance_to_station = calculate_distance(
                route_stations[last_stop_index].latitude,
                route_stations[last_stop_index].longitude,
                station.latitude,
                station.longitude
            )
            
            if distance_to_station <= current_range:
                # Score based on price and distance (lower is better)
                score = station.price + (distance_to_station / max_range) * 10
                if score < best_score:
                    best_score = score
                    best_station = station
                    best_station_index = i
        
        if best_station:
            optimal_stops.append(best_station)
            distance_covered += calculate_distance(
                route_stations[last_stop_index].latitude,
                route_stations[last_stop_index].longitude,
                best_station.latitude,
                best_station.longitude
            )
            current_range = max_range
            last_stop_index = best_station_index
        else:
            break
            
    return optimal_stops

def calculate_fuel_cost(optimal_stops: List[FuelStation], total_distance: float, 
                       mpg: float = 10) -> float:
    """Calculate total fuel cost based on optimal stops"""
    total_gallons = total_distance / mpg
    avg_price = sum(station.price for station in optimal_stops) / len(optimal_stops)
    return total_gallons * avg_price


# calculate distance between two locations coordinates using Haversine formula
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    R = 3959.87433  # Earth's radius in miles

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance
