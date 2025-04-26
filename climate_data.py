import json
import pandas as pd
import random
import os

def get_climate_data(lat, lon):
    """
    Get climate data for a specific location.
    In a production app, this would use real API calls to weather/climate services.
    
    Args:
        lat (float): Latitude of the location
        lon (float): Longitude of the location
        
    Returns:
        dict: Climate data including temperature, rainfall, humidity, etc.
    """
    # In a real implementation, we would use the OpenMeteo API
    # For this example, we simulate climate data based on the latitude
    # This is a simplified model and would be replaced with actual API calls
    
    # Use latitude to estimate climate zone
    if abs(lat) < 15:
        climate_zone = "Tropical"
        avg_temp = random.uniform(24, 28)
        annual_rainfall = random.uniform(1500, 3000)
        humidity = random.uniform(70, 90)
    elif abs(lat) < 30:
        climate_zone = "Subtropical"
        avg_temp = random.uniform(18, 25)
        annual_rainfall = random.uniform(800, 1500)
        humidity = random.uniform(50, 70)
    else:
        climate_zone = "Temperate"
        avg_temp = random.uniform(10, 18)
        annual_rainfall = random.uniform(600, 1200)
        humidity = random.uniform(40, 60)
    
    # Create climate data dictionary
    climate_data = {
        "climate_zone": climate_zone,
        "avg_temp": round(avg_temp, 1),
        "annual_rainfall": round(annual_rainfall, 0),
        "humidity": round(humidity, 0),
        "pollution_level": random.choice(["Low", "Medium", "High"]),
        "sunshine_hours": round(random.uniform(4, 8), 1)
    }
    
    return climate_data

def get_climate_zones():
    """
    Returns a list of climate zones and their characteristics.
    
    Returns:
        list: List of climate zones with details
    """
    climate_zones = [
        {
            "name": "Tropical",
            "description": "Hot and humid climate with high rainfall, typically found near the equator.",
            "avg_temp_range": "24-28°C",
            "rainfall_range": "1500-3000mm",
            "suitable_trees": ["Neem", "Banyan", "Peepal", "Mango", "Jamun"]
        },
        {
            "name": "Subtropical",
            "description": "Warm climate with distinct wet and dry seasons, found in regions near the Tropics.",
            "avg_temp_range": "18-25°C",
            "rainfall_range": "800-1500mm",
            "suitable_trees": ["Neem", "Gulmohar", "Ashoka", "Amaltas", "Silver Oak"]
        },
        {
            "name": "Temperate",
            "description": "Moderate climate with distinct seasons, typically found in mid-latitudes.",
            "avg_temp_range": "10-18°C",
            "rainfall_range": "600-1200mm",
            "suitable_trees": ["Silver Oak", "Eucalyptus", "Amla", "Pine", "Oak"]
        },
        {
            "name": "Arid",
            "description": "Hot, dry climate with minimal rainfall, found in desert regions.",
            "avg_temp_range": "20-30°C",
            "rainfall_range": "100-300mm",
            "suitable_trees": ["Neem", "Eucalyptus", "Acacia", "Desert Date", "Ghaf"]
        }
    ]
    
    return climate_zones
