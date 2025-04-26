import pandas as pd

def get_tree_data():
    """
    Returns a dataset of tree species with their characteristics and suitability factors.
    In a production environment, this would be fetched from a database.
    """
    trees = [
        {
            "id": 1,
            "name": "Neem",
            "scientific_name": "Azadirachta indica",
            "growth_rate": "Medium",
            "mature_height": "15-20 m",
            "lifespan": "150-200 years",
            "native_region": "Indian Subcontinent",
            "climate_suitability": ["Tropical", "Subtropical"],
            "soil_suitability": ["Loamy", "Sandy", "Clay"],
            "drought_tolerance": "High",
            "water_needs": "Low",
            "environmental_benefits": "Excellent air purifier, natural pest repellent, medicinal properties",
            "purposes": ["Air Purification", "Shade", "Medicinal", "Carbon Sequestration"],
            "maintenance_level": "Low"
        },
        {
            "id": 2,
            "name": "Banyan",
            "scientific_name": "Ficus benghalensis",
            "growth_rate": "Medium",
            "mature_height": "20-30 m",
            "lifespan": "200-300 years",
            "native_region": "Indian Subcontinent",
            "climate_suitability": ["Tropical", "Subtropical"],
            "soil_suitability": ["Loamy", "Clay"],
            "drought_tolerance": "Medium",
            "water_needs": "Medium",
            "environmental_benefits": "Significant carbon sequestration, habitat for wildlife, soil conservation",
            "purposes": ["Shade", "Biodiversity", "Carbon Sequestration"],
            "maintenance_level": "Medium"
        },
        {
            "id": 3,
            "name": "Arjuna",
            "scientific_name": "Terminalia arjuna",
            "growth_rate": "Medium",
            "mature_height": "20-25 m",
            "lifespan": "100-150 years",
            "native_region": "Indian Subcontinent",
            "climate_suitability": ["Tropical", "Subtropical"],
            "soil_suitability": ["Loamy", "Sandy", "Riverbed"],
            "drought_tolerance": "Medium",
            "water_needs": "Medium",
            "environmental_benefits": "Strong carbon sequestration, supports riparian ecosystems, medicinal bark",
            "purposes": ["Medicinal", "Biodiversity", "Carbon Sequestration", "Erosion Control"],
            "maintenance_level": "Low"
        },
        {
            "id": 4,
            "name": "Peepal",
            "scientific_name": "Ficus religiosa",
            "growth_rate": "Fast",
            "mature_height": "20-30 m",
            "lifespan": "100-150 years",
            "native_region": "Indian Subcontinent",
            "climate_suitability": ["Tropical", "Subtropical"],
            "soil_suitability": ["Loamy", "Sandy", "Clay"],
            "drought_tolerance": "High",
            "water_needs": "Low",
            "environmental_benefits": "Exceptional oxygen production, significant carbon sequestration, habitat for wildlife",
            "purposes": ["Air Purification", "Shade", "Biodiversity", "Carbon Sequestration"],
            "maintenance_level": "Low"
        },
        {
            "id": 5,
            "name": "Gulmohar",
            "scientific_name": "Delonix regia",
            "growth_rate": "Fast",
            "mature_height": "10-15 m",
            "lifespan": "40-50 years",
            "native_region": "Madagascar",
            "climate_suitability": ["Tropical", "Subtropical"],
            "soil_suitability": ["Loamy", "Sandy"],
            "drought_tolerance": "High",
            "water_needs": "Low",
            "environmental_benefits": "Provides shade, reduces heat island effect, ornamental value",
            "purposes": ["Shade", "Ornamental", "Air Purification"],
            "maintenance_level": "Medium"
        },
        {
            "id": 6,
            "name": "Ashoka",
            "scientific_name": "Saraca asoca",
            "growth_rate": "Slow",
            "mature_height": "6-9 m",
            "lifespan": "60-80 years",
            "native_region": "Indian Subcontinent",
            "climate_suitability": ["Tropical", "Subtropical"],
            "soil_suitability": ["Loamy", "Clay"],
            "drought_tolerance": "Low",
            "water_needs": "High",
            "environmental_benefits": "Air purification, medicinal properties, ornamental value",
            "purposes": ["Medicinal", "Ornamental", "Air Purification"],
            "maintenance_level": "Medium"
        },
        {
            "id": 7,
            "name": "Mango",
            "scientific_name": "Mangifera indica",
            "growth_rate": "Medium",
            "mature_height": "10-15 m",
            "lifespan": "100-200 years",
            "native_region": "Indian Subcontinent",
            "climate_suitability": ["Tropical", "Subtropical"],
            "soil_suitability": ["Loamy", "Sandy", "Clay"],
            "drought_tolerance": "Medium",
            "water_needs": "Medium",
            "environmental_benefits": "Fruit production, carbon sequestration, habitat for birds",
            "purposes": ["Fruit Production", "Shade", "Biodiversity"],
            "maintenance_level": "High"
        },
        {
            "id": 8,
            "name": "Amaltas",
            "scientific_name": "Cassia fistula",
            "growth_rate": "Medium",
            "mature_height": "8-15 m",
            "lifespan": "50-100 years",
            "native_region": "Indian Subcontinent",
            "climate_suitability": ["Tropical", "Subtropical"],
            "soil_suitability": ["Loamy", "Sandy"],
            "drought_tolerance": "High",
            "water_needs": "Low",
            "environmental_benefits": "Nitrogen fixation, medicinal properties, ornamental value",
            "purposes": ["Medicinal", "Ornamental", "Soil Improvement"],
            "maintenance_level": "Low"
        },
        {
            "id": 9,
            "name": "Jamun",
            "scientific_name": "Syzygium cumini",
            "growth_rate": "Medium",
            "mature_height": "10-15 m",
            "lifespan": "80-100 years",
            "native_region": "Indian Subcontinent",
            "climate_suitability": ["Tropical", "Subtropical"],
            "soil_suitability": ["Loamy", "Sandy", "Clay"],
            "drought_tolerance": "Medium",
            "water_needs": "Medium",
            "environmental_benefits": "Fruit production, carbon sequestration, erosion control",
            "purposes": ["Fruit Production", "Shade", "Carbon Sequestration"],
            "maintenance_level": "Medium"
        },
        {
            "id": 10,
            "name": "Amla",
            "scientific_name": "Phyllanthus emblica",
            "growth_rate": "Medium",
            "mature_height": "8-18 m",
            "lifespan": "60-70 years",
            "native_region": "Indian Subcontinent",
            "climate_suitability": ["Tropical", "Subtropical", "Temperate"],
            "soil_suitability": ["Loamy", "Sandy", "Rocky"],
            "drought_tolerance": "High",
            "water_needs": "Low",
            "environmental_benefits": "Medicinal fruit, soil improvement, hardy in poor conditions",
            "purposes": ["Fruit Production", "Medicinal", "Soil Improvement"],
            "maintenance_level": "Low"
        },
        {
            "id": 11,
            "name": "Silver Oak",
            "scientific_name": "Grevillea robusta",
            "growth_rate": "Fast",
            "mature_height": "18-35 m",
            "lifespan": "60-80 years",
            "native_region": "Australia",
            "climate_suitability": ["Tropical", "Subtropical", "Temperate"],
            "soil_suitability": ["Loamy", "Sandy"],
            "drought_tolerance": "High",
            "water_needs": "Low",
            "environmental_benefits": "Windbreak, erosion control, timber production",
            "purposes": ["Windbreak", "Shade", "Timber"],
            "maintenance_level": "Low"
        },
        {
            "id": 12,
            "name": "Eucalyptus",
            "scientific_name": "Eucalyptus globulus",
            "growth_rate": "Fast",
            "mature_height": "30-55 m",
            "lifespan": "50-100 years",
            "native_region": "Australia",
            "climate_suitability": ["Tropical", "Subtropical", "Temperate"],
            "soil_suitability": ["Loamy", "Sandy", "Clay"],
            "drought_tolerance": "High",
            "water_needs": "Low",
            "environmental_benefits": "Fast carbon sequestration, timber, medicinal oil",
            "purposes": ["Carbon Sequestration", "Timber", "Medicinal"],
            "maintenance_level": "Low"
        }
    ]
    
    return trees

def get_tree_details(tree_name):
    """
    Returns detailed information about a specific tree.
    
    Args:
        tree_name (str): The name of the tree to get details for
        
    Returns:
        dict: Tree details or None if not found
    """
    trees = get_tree_data()
    for tree in trees:
        if tree["name"].lower() == tree_name.lower():
            return tree
    return None
