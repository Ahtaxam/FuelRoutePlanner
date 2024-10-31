# FuelRoutePlanner

FuelRoutePlanner is a Django-based API that calculates optimal driving routes across the USA. It identifies cost-effective fuel stops along the route based on fuel prices and the vehicle's range, helping users save on fuel costs while planning long-distance trips.

## Features
- Calculates optimized driving routes using the OpenRouteService API.
- Identifies fuel stops along the route based on cost-effectiveness.
- Estimates total fuel costs based on distance, vehicle efficiency, and fuel prices.
- Accepts start and end locations within the USA.

## Prerequisites
- **Python 3.x**
- **Django**
- **requests** library (for handling API requests)
- An API key for **OpenRouteService** (for routing and geocoding)

## Getting Started

### 1. Clone the Repository
First, clone the repository to your local machine:

```bash
git clone https://github.com/Ahtaxam/FuelRoutePlanner.git
cd FuelRoutePlanner
```


## 2. Set Up a Virtual Environment
It’s recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

## 3. Install Dependencies
Install all the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## 4. Set Up Environment Variables
Create a .env file in the project root to securely store your API keys. Add your OpenRouteService API key like so:
```bash
OPENROUTESERVICE_API_KEY= your_api_key_here
OPENROUTESERVICE_COORDINATE_URL= api url to get coordinated
OPENROUTESERVICE_ROUTE_URL = api url to get routes
```

## 5. Run the Server
Start the Django development server:
```bash
python manage.py runserver
```

## 6. Test the API
You can test the API by sending POST requests to the **/optimize-route** endpoint with JSON input specifying start_location and end_location:
```bash
{
    "start_location": "New York, NY",
    "end_location": "Los Angeles, CA"
}

```

# Future Enhancements
Some potential future improvements to the project include:

- Real-time fuel price integration.
- Enhanced mapping services for more accurate route details.
- User accounts for saving routes and setting fuel preferences.



**This `README.md` includes all the necessary information for a user or developer to understand the purpose of the project, install it, and run it locally. Let me know if you need more details or any additional sections!**
