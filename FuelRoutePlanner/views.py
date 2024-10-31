from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import os
from .utils.helpers import find_stations_along_route, find_optimal_fuel_stops, calculate_fuel_cost
from .utils.load_data import load_fuel_stations
from dotenv import load_dotenv

load_dotenv()



# This will be called by the frontend on POST request
@csrf_exempt
def optimized_routes(request):
    if request.method == 'POST':
        
        try:
            data = json.loads(request.body)
            start_location = data.get('start_location')
            end_location = data.get('end_location')
            OPENROUTESERVICE_API_KEY = os.environ['OPENROUTESERVICE_API_KEY']
            OPENROUTESERVICE_COORDINATE_URL = os.environ['OPENROUTESERVICE_COORDINATE_URL']
            OPENROUTESERVICE_ROUTE_URL = os.environ['OPENROUTESERVICE_ROUTE_URL']
            

            # Get coordinates for start and end locations
            def get_coordinates(location):
                url = OPENROUTESERVICE_COORDINATE_URL
                params = {
                    'api_key': OPENROUTESERVICE_API_KEY, 
                    'text': location,
                    'size': 1
                }
                response = requests.get(url, params=params)
                data = response.json()
                if data['features']:
                    coordinates = data['features'][0]['geometry']['coordinates']
                    return coordinates[1], coordinates[0]  # lat, lon
                return None

            start_coordinates = get_coordinates(start_location)
            end_coordinates = get_coordinates(end_location)

            if not start_coordinates or not end_coordinates:
                return JsonResponse({'error': 'Invalid locations'}, status=400)

            # Get route from OpenRouteService using the above coordinates
            url = OPENROUTESERVICE_ROUTE_URL
            params = {
                'api_key': OPENROUTESERVICE_API_KEY,
                'start': f'{start_coordinates[1]},{start_coordinates[0]}',
                'end': f'{end_coordinates[1]},{end_coordinates[0]}'
            }

            response = requests.get(url, params=params)  
            route_data = response.json()

            # Extract route information
            coordinates = route_data['features'][0]['geometry']['coordinates']

            # get total distance between the start and end
            total_distance = route_data['features'][0]['properties']['summary']['distance'] * 0.000621371  # meters to miles

            # Load and process fuel stations
            all_stations = load_fuel_stations()

            # this will find stations along the route
            route_stations = find_stations_along_route(coordinates, all_stations)
            # After finding the stations, find the optimal fuel stops
            optimal_stops = find_optimal_fuel_stops(route_stations, total_distance)

            # Calculate total fuel cost based on optimal stops
            total_fuel_cost = calculate_fuel_cost(optimal_stops, total_distance)

            # Prepare response data
            response_data = {
                'route': {
                    'coordinates': coordinates,
                    'total_distance': round(total_distance, 2),
                    'total_fuel_cost': round(total_fuel_cost, 2)
                },
                'fuel_stops': [station.to_dict() for station in optimal_stops]
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
















