import pandas as pd
from tree_data import get_tree_data

def get_recommendations(climate_data, soil_data):
    """
    Generates tree recommendations based on climate and soil data.
    
    Args:
        climate_data (dict): Climate data for the location
        soil_data (dict): Soil data for the location
        
    Returns:
        list: List of recommended tree species
    """
    # Get all available trees
    all_trees = get_tree_data()
    
    # Filter trees based on climate suitability
    climate_suitable_trees = []
    for tree in all_trees:
        if climate_data["climate_zone"] in tree["climate_suitability"]:
            climate_suitable_trees.append(tree)
    
    # Further filter based on soil suitability
    soil_suitable_trees = []
    for tree in climate_suitable_trees:
        if soil_data["soil_type"] in tree["soil_suitability"]:
            soil_suitable_trees.append(tree)
    
    # If we have too few recommendations, relax soil constraints
    if len(soil_suitable_trees) < 3:
        return climate_suitable_trees
    
    # Score each tree based on environmental conditions
    scored_trees = []
    for tree in soil_suitable_trees:
        score = 0
        
        # Score based on drought tolerance if in dry area
        if climate_data["annual_rainfall"] < 800:  # Low rainfall
            if tree["drought_tolerance"] == "High":
                score += 3
            elif tree["drought_tolerance"] == "Medium":
                score += 1
        
        # Score based on water needs if in wet area
        if climate_data["annual_rainfall"] > 1500:  # High rainfall
            if tree["water_needs"] == "High":
                score += 2
            elif tree["water_needs"] == "Medium":
                score += 1
        
        # Score based on pollution levels (if available)
        if "pollution_level" in climate_data:
            if climate_data["pollution_level"] == "High" and "Air Purification" in tree["purposes"]:
                score += 3
        
        # Add the scored tree
        tree_with_score = tree.copy()
        tree_with_score["recommendation_score"] = score
        scored_trees.append(tree_with_score)
    
    # Sort trees by score
    sorted_trees = sorted(scored_trees, key=lambda x: x["recommendation_score"], reverse=True)
    
    # Return top recommendations
    return sorted_trees
