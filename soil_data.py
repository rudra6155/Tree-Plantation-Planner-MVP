import pandas as pd
import random

def get_soil_types():
    """
    Returns a list of soil types and their characteristics.
    
    Returns:
        list: List of soil types with details
    """
    soil_types = [
        {
            "name": "Sandy",
            "description": "Sandy soil has large particles and feels gritty. It drains quickly but doesn't hold nutrients well.",
            "water_retention": "Low",
            "nutrient_content": "Low",
            "suitable_trees": ["Neem", "Eucalyptus", "Acacia", "Amla", "Amaltas"]
        },
        {
            "name": "Loamy",
            "description": "Loamy soil has medium-sized particles and feels crumbly. It has good drainage while retaining moisture and nutrients.",
            "water_retention": "Medium",
            "nutrient_content": "High",
            "suitable_trees": ["Most trees", "Ideal for majority of species"]
        },
        {
            "name": "Clay",
            "description": "Clay soil has small particles and feels sticky when wet. It retains water and nutrients well but drains poorly.",
            "water_retention": "High",
            "nutrient_content": "High",
            "suitable_trees": ["Neem", "Banyan", "Peepal", "Jamun", "Arjuna"]
        },
        {
            "name": "Silty",
            "description": "Silty soil has medium to small particles and feels smooth. It holds moisture well but can be compacted easily.",
            "water_retention": "Medium-High",
            "nutrient_content": "Medium",
            "suitable_trees": ["Neem", "Mango", "Jamun", "Arjuna", "Ashoka"]
        },
        {
            "name": "Rocky",
            "description": "Rocky soil contains stones and rocks with little fine material. It drains quickly and doesn't hold nutrients well.",
            "water_retention": "Very Low",
            "nutrient_content": "Low",
            "suitable_trees": ["Amla", "Silver Oak", "Eucalyptus", "Pine"]
        },
        {
            "name": "Riverbed",
            "description": "Soil found near rivers, typically a mix of sand, silt, and organic matter. It's usually fertile and well-drained.",
            "water_retention": "Medium",
            "nutrient_content": "High",
            "suitable_trees": ["Arjuna", "Jamun", "Banyan", "Peepal", "Mango"]
        }
    ]
    
    return soil_types

def get_soil_data(lat, lon):
    """
    Get soil data for a specific location.
    In a production app, this would use real API calls to soil/geological services.
    
    Args:
        lat (float): Latitude of the location
        lon (float): Longitude of the location
        
    Returns:
        dict: Soil data including soil type, pH level, drainage, etc.
    """
    # In a real implementation, we would use an appropriate soil database or API
    # For this example, we'll generate simulated data based on the coordinates
    
    # Pseudo-random selection based on coordinates
    soil_options = ["Sandy", "Loamy", "Clay", "Silty", "Rocky", "Riverbed"]
    drainage_options = ["Poor", "Moderate", "Good", "Excellent"]
    nutrient_options = ["Low", "Medium", "High"]
    
    # Use coordinates to seed random selection
    # This is just for demonstration - in a real app, use actual soil data services
    seed = int(abs(lat * 100 + lon * 100))
    random.seed(seed)
    
    soil_type = random.choice(soil_options)
    
    # Assign related properties based on soil type
    if soil_type == "Sandy":
        drainage = "Excellent"
        nutrient_level = "Low"
    elif soil_type == "Loamy":
        drainage = "Good"
        nutrient_level = "High"
    elif soil_type == "Clay":
        drainage = "Poor"
        nutrient_level = "High"
    elif soil_type == "Silty":
        drainage = "Moderate"
        nutrient_level = "Medium"
    elif soil_type == "Rocky":
        drainage = "Excellent"
        nutrient_level = "Low"
    else:  # Riverbed
        drainage = "Good"
        nutrient_level = "High"
    
    # Randomize pH level but keep it realistic
    if soil_type in ["Sandy", "Rocky"]:
        ph_level = round(random.uniform(5.5, 7.0), 1)
    elif soil_type in ["Clay", "Loamy"]:
        ph_level = round(random.uniform(6.0, 7.5), 1)
    else:
        ph_level = round(random.uniform(6.0, 7.0), 1)
    
    # Create soil data dictionary
    soil_data = {
        "soil_type": soil_type,
        "ph_level": ph_level,
        "drainage": drainage,
        "nutrient_level": nutrient_level,
        "texture": get_soil_texture(soil_type)
    }
    
    return soil_data

def get_soil_texture(soil_type):
    """
    Returns the texture description for a given soil type.
    
    Args:
        soil_type (str): The type of soil
        
    Returns:
        str: Description of soil texture
    """
    textures = {
        "Sandy": "Gritty with large particles",
        "Loamy": "Crumbly with medium-sized particles",
        "Clay": "Sticky when wet, hard when dry",
        "Silty": "Smooth and flour-like when dry",
        "Rocky": "Contains stones and little fine material",
        "Riverbed": "Mixed texture with sand and silt"
    }
    
    return textures.get(soil_type, "Unknown texture")
