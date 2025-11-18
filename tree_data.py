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
def get_balcony_plants_data():
    """Returns dataset of balcony-friendly plants"""
    balcony_plants = [
        {
            'name': 'Snake Plant (Sansevieria)',
            'scientific_name': 'Dracaena trifasciata',
            'space_required': 'Very Small',
            'sunlight_need': 'Low (2-6 hours)',
            'watering': 'Once every 2-3 weeks',
            'purposes': ['Air Purification', 'Low Maintenance'],
            'care_difficulty': 'Very Easy',
            'growth_rate': 'Slow',
            'max_height': '1-3 feet',
            'benefits': 'Removes toxins, produces oxygen at night',
            'ideal_for': 'Beginners, Low-light spaces',
            'pot_size': '6-8 inches',
            'indoor_ok': True
        },
        {
            'name': 'Tulsi (Holy Basil)',
            'scientific_name': 'Ocimum sanctum',
            'space_required': 'Small',
            'sunlight_need': 'High (6+ hours)',
            'watering': 'Daily (moderate)',
            'purposes': ['Medicinal', 'Edible', 'Air Purification'],
            'care_difficulty': 'Easy',
            'growth_rate': 'Fast',
            'max_height': '1-2 feet',
            'benefits': 'Anti-inflammatory, stress relief, air purifier',
            'ideal_for': 'Sunny balconies',
            'pot_size': '8-10 inches',
            'indoor_ok': False
        },
        {
            'name': 'Money Plant (Pothos)',
            'scientific_name': 'Epipremnum aureum',
            'space_required': 'Very Small',
            'sunlight_need': 'Low to Medium (2-6 hours)',
            'watering': 'Twice a week',
            'purposes': ['Air Purification', 'Aesthetic/Decor', 'Low Maintenance'],
            'care_difficulty': 'Very Easy',
            'growth_rate': 'Fast',
            'max_height': 'Vine (can grow 10+ feet)',
            'benefits': 'Removes formaldehyde, easy propagation',
            'ideal_for': 'Hanging baskets, climbers',
            'pot_size': '6-8 inches',
            'indoor_ok': True
        },
        {
            'name': 'Aloe Vera',
            'scientific_name': 'Aloe barbadensis',
            'space_required': 'Small',
            'sunlight_need': 'High (6+ hours)',
            'watering': 'Once every 2 weeks',
            'purposes': ['Medicinal', 'Low Maintenance'],
            'care_difficulty': 'Easy',
            'growth_rate': 'Slow',
            'max_height': '1-2 feet',
            'benefits': 'Skin healing, air purification',
            'ideal_for': 'Sunny spots, dry climates',
            'pot_size': '8-10 inches',
            'indoor_ok': True
        },
        {
            'name': 'Mint (Pudina)',
            'scientific_name': 'Mentha',
            'space_required': 'Small',
            'sunlight_need': 'Medium (4-6 hours)',
            'watering': 'Daily',
            'purposes': ['Edible', 'Medicinal'],
            'care_difficulty': 'Easy',
            'growth_rate': 'Fast',
            'max_height': '1-1.5 feet',
            'benefits': 'Culinary herb, digestive aid',
            'ideal_for': 'Kitchen gardens',
            'pot_size': '8-10 inches',
            'indoor_ok': False
        },
        {
            'name': 'Spider Plant',
            'scientific_name': 'Chlorophytum comosum',
            'space_required': 'Small',
            'sunlight_need': 'Low to Medium (2-6 hours)',
            'watering': '2-3 times a week',
            'purposes': ['Air Purification', 'Low Maintenance', 'Aesthetic/Decor'],
            'care_difficulty': 'Very Easy',
            'growth_rate': 'Medium',
            'max_height': '1-2 feet',
            'benefits': 'Removes CO and formaldehyde',
            'ideal_for': 'Beginners, hanging baskets',
            'pot_size': '6-8 inches',
            'indoor_ok': True
        },
        {
            'name': 'Coriander (Dhania)',
            'scientific_name': 'Coriandrum sativum',
            'space_required': 'Small',
            'sunlight_need': 'Medium (4-6 hours)',
            'watering': 'Daily (light)',
            'purposes': ['Edible'],
            'care_difficulty': 'Easy',
            'growth_rate': 'Fast',
            'max_height': '1-1.5 feet',
            'benefits': 'Fresh herbs, kitchen garden',
            'ideal_for': 'Balcony herb gardens',
            'pot_size': '8-10 inches',
            'indoor_ok': False
        },
        {
            'name': 'Peace Lily',
            'scientific_name': 'Spathiphyllum',
            'space_required': 'Small to Medium',
            'sunlight_need': 'Low (2-4 hours)',
            'watering': 'Weekly',
            'purposes': ['Air Purification', 'Aesthetic/Decor'],
            'care_difficulty': 'Easy',
            'growth_rate': 'Slow',
            'max_height': '1-2 feet',
            'benefits': 'Removes toxins, beautiful flowers',
            'ideal_for': 'Low-light indoors',
            'pot_size': '8-10 inches',
            'indoor_ok': True
        },
        {
            'name': 'Tomato (Dwarf Variety)',
            'scientific_name': 'Solanum lycopersicum',
            'space_required': 'Medium',
            'sunlight_need': 'High (6-8 hours)',
            'watering': 'Daily',
            'purposes': ['Edible'],
            'care_difficulty': 'Medium',
            'growth_rate': 'Fast',
            'max_height': '2-3 feet',
            'benefits': 'Fresh vegetables',
            'ideal_for': 'Sunny balconies, vegetable gardens',
            'pot_size': '12-14 inches',
            'indoor_ok': False
        },
        {
            'name': 'Areca Palm',
            'scientific_name': 'Dypsis lutescens',
            'space_required': 'Medium to Large',
            'sunlight_need': 'Medium (4-6 hours)',
            'watering': '3 times a week',
            'purposes': ['Air Purification', 'Aesthetic/Decor'],
            'care_difficulty': 'Medium',
            'growth_rate': 'Medium',
            'max_height': '4-6 feet',
            'benefits': 'Humidifies air, removes toxins',
            'ideal_for': 'Large balconies, living rooms',
            'pot_size': '14-16 inches',
            'indoor_ok': True
        }
    ]
    return balcony_plants
