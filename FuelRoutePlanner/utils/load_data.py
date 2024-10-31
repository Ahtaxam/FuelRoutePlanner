from typing import List, Dict
import pandas as pd

class FuelStation:
    def __init__(self, name: str, latitude: float, longitude: float, price: float, address: str):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.price = price
        self.address = address

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'price': self.price,
            'address': self.address
        }


# This will load the fuel stations from the CSV file
# I have calculated the latitude and longitude from the address
def load_fuel_stations() -> List[FuelStation]:
    """Load fuel stations from CSV file"""
    df = pd.read_csv('FuelRoutePlanner/fuel_stations.csv') 
    stations = []
    
    for _, row in df.iterrows():
        station = FuelStation(
            name=row['Truckstop Name'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            price=row['Retail Price'],
            address=row['Address']
        )
        stations.append(station)
    
    
    return stations