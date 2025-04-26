def calculate_impact(planted_trees):
    """
    Calculate the environmental impact of planted trees.
    
    Args:
        planted_trees (list): List of tracked trees
        
    Returns:
        dict: Environmental impact metrics
    """
    # Initialize impact metrics
    carbon_sequestered = 0
    oxygen_produced = 0
    pollutants_removed = 0
    
    # Calculate impact for each tree
    for tree in planted_trees:
        # Base values per tree (kg per year)
        # These are simplified estimates - real values would depend on species, age, size, etc.
        base_carbon = get_base_carbon(tree['name'])
        base_oxygen = get_base_oxygen(tree['name'])
        base_pollutants = get_base_pollutants(tree['name'])
        
        # Adjust based on tree status/growth stage
        growth_factor = get_growth_factor(tree['status'])
        
        # Add to total impact
        carbon_sequestered += base_carbon * growth_factor
        oxygen_produced += base_oxygen * growth_factor
        pollutants_removed += base_pollutants * growth_factor
    
    # Return impact data
    return {
        "carbon_sequestered": carbon_sequestered,
        "oxygen_produced": oxygen_produced,
        "pollutants_removed": pollutants_removed
    }

def get_base_carbon(tree_name):
    """
    Get base carbon sequestration value for a tree species (kg per year).
    
    Args:
        tree_name (str): Name of the tree species
        
    Returns:
        float: Base carbon sequestration value
    """
    # These values are simplified estimates
    carbon_values = {
        "Neem": 15.3,
        "Banyan": 22.1,
        "Arjuna": 16.5,
        "Peepal": 21.2,
        "Gulmohar": 12.8,
        "Ashoka": 10.2,
        "Mango": 14.7,
        "Amaltas": 11.6,
        "Jamun": 13.9,
        "Amla": 10.8,
        "Silver Oak": 18.4,
        "Eucalyptus": 20.6
    }
    
    # Return value for the tree or default value if not found
    return carbon_values.get(tree_name, 15.0)

def get_base_oxygen(tree_name):
    """
    Get base oxygen production value for a tree species (kg per year).
    
    Args:
        tree_name (str): Name of the tree species
        
    Returns:
        float: Base oxygen production value
    """
    # These values are simplified estimates
    oxygen_values = {
        "Neem": 20.7,
        "Banyan": 29.8,
        "Arjuna": 22.3,
        "Peepal": 28.6,
        "Gulmohar": 17.3,
        "Ashoka": 13.8,
        "Mango": 19.8,
        "Amaltas": 15.7,
        "Jamun": 18.7,
        "Amla": 14.6,
        "Silver Oak": 24.8,
        "Eucalyptus": 27.8
    }
    
    # Return value for the tree or default value if not found
    return oxygen_values.get(tree_name, 20.0)

def get_base_pollutants(tree_name):
    """
    Get base pollutant removal value for a tree species (grams per year).
    
    Args:
        tree_name (str): Name of the tree species
        
    Returns:
        float: Base pollutant removal value
    """
    # These values are simplified estimates
    pollutant_values = {
        "Neem": 135.6,
        "Banyan": 187.5,
        "Arjuna": 124.8,
        "Peepal": 173.4,
        "Gulmohar": 95.2,
        "Ashoka": 82.6,
        "Mango": 108.3,
        "Amaltas": 91.4,
        "Jamun": 103.7,
        "Amla": 87.2,
        "Silver Oak": 132.8,
        "Eucalyptus": 128.5
    }
    
    # Return value for the tree or default value if not found
    return pollutant_values.get(tree_name, 100.0)

def get_growth_factor(status):
    """
    Get growth factor based on tree growth stage.
    
    Args:
        status (str): Current growth stage of the tree
        
    Returns:
        float: Growth factor multiplier
    """
    # Growth factors based on tree stage
    factors = {
        "Newly Planted": 0.1,
        "Seedling": 0.3,
        "Sapling": 0.5,
        "Young Tree": 0.8,
        "Mature Tree": 1.0
    }
    
    # Return factor for the status or default factor if not found
    return factors.get(status, 0.5)
