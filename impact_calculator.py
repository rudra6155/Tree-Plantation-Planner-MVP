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
        growth_factor = get_growth_factor(tree.get('status', 'Newly Planted'))

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
        # OUTDOOR TREES (Original 12)
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
        "Eucalyptus": 20.6,

        # OUTDOOR TREES (New additions from tree_data.py)
        "Guava (Amrood)": 12.5,
        "Papaya (Papita)": 10.0,
        "Pomegranate (Anar)": 11.0,
        "Drumstick (Moringa)": 17.5,
        "Curry Tree (Kadi Patta)": 9.0,
        "Jackfruit": 28.0,
        "Coconut Palm": 32.0,
        "Neem (Outdoor)": 15.3,
        "Bamboo": 35.0,
        "Rain Tree (Samanea)": 24.0,
        "Gulmohar (Flame Tree)": 12.8,
        "Jacaranda": 14.0,
        "Bakul (Mimusops)": 13.5,

        # BALCONY/INDOOR PLANTS (Smaller carbon impact)
        "Snake Plant (Sansevieria)": 2.0,
        "Tulsi (Holy Basil)": 1.5,
        "Money Plant (Pothos)": 1.8,
        "Aloe Vera": 1.2,
        "Mint (Pudina)": 0.8,
        "Spider Plant": 1.6,
        "Coriander (Dhania)": 0.5,
        "Peace Lily": 1.9,
        "Tomato (Dwarf Variety)": 1.0,
        "Areca Palm": 3.5,
        "Curry Leaves (Kadi Patta)": 2.2,
        "Jade Plant": 1.1,
        "Rubber Plant": 3.0,
        "Boston Fern": 1.7,

        # MEDICINAL PLANTS (New additions)
        "Lavender": 0.9,
        "Rosemary": 1.0,
        "Brahmi (Bacopa)": 0.7,
        "Ashwagandha (Indian Ginseng)": 1.3,
        "Stevia (Sweet Leaf)": 0.8,
        "Lemongrass (Hari Chai Patti)": 1.4,
        "Ajwain (Carom Plant)": 0.6,
        "Methi (Fenugreek)": 0.5,
        "Ginger (Adrak)": 1.1,
        "Turmeric (Haldi)": 1.2,
        "Insulin Plant (Costus)": 1.5,
        "Hibiscus (Gudhal)": 2.8,
        "English Ivy": 1.6,
    }

    # Return value for the tree or default value if not found
    return carbon_values.get(tree_name, 5.0)


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
        # OUTDOOR TREES (Original 12)
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
        "Eucalyptus": 27.8,

        # OUTDOOR TREES (New additions)
        "Guava (Amrood)": 16.8,
        "Papaya (Papita)": 13.5,
        "Pomegranate (Anar)": 14.8,
        "Drumstick (Moringa)": 23.6,
        "Curry Tree (Kadi Patta)": 12.1,
        "Jackfruit": 37.8,
        "Coconut Palm": 43.2,
        "Neem (Outdoor)": 20.7,
        "Bamboo": 47.2,
        "Rain Tree (Samanea)": 32.4,
        "Gulmohar (Flame Tree)": 17.3,
        "Jacaranda": 18.9,
        "Bakul (Mimusops)": 18.2,

        # BALCONY/INDOOR PLANTS
        "Snake Plant (Sansevieria)": 2.7,
        "Tulsi (Holy Basil)": 2.0,
        "Money Plant (Pothos)": 2.4,
        "Aloe Vera": 1.6,
        "Mint (Pudina)": 1.1,
        "Spider Plant": 2.2,
        "Coriander (Dhania)": 0.7,
        "Peace Lily": 2.6,
        "Tomato (Dwarf Variety)": 1.4,
        "Areca Palm": 4.7,
        "Curry Leaves (Kadi Patta)": 3.0,
        "Jade Plant": 1.5,
        "Rubber Plant": 4.0,
        "Boston Fern": 2.3,

        # MEDICINAL PLANTS
        "Lavender": 1.2,
        "Rosemary": 1.4,
        "Brahmi (Bacopa)": 0.9,
        "Ashwagandha (Indian Ginseng)": 1.8,
        "Stevia (Sweet Leaf)": 1.1,
        "Lemongrass (Hari Chai Patti)": 1.9,
        "Ajwain (Carom Plant)": 0.8,
        "Methi (Fenugreek)": 0.7,
        "Ginger (Adrak)": 1.5,
        "Turmeric (Haldi)": 1.6,
        "Insulin Plant (Costus)": 2.0,
        "Hibiscus (Gudhal)": 3.8,
        "English Ivy": 2.2,
    }

    # Return value for the tree or default value if not found
    return oxygen_values.get(tree_name, 8.0)


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
        # OUTDOOR TREES (Original 12)
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
        "Eucalyptus": 128.5,

        # OUTDOOR TREES (New additions)
        "Guava (Amrood)": 98.5,
        "Papaya (Papita)": 75.0,
        "Pomegranate (Anar)": 85.3,
        "Drumstick (Moringa)": 142.0,
        "Curry Tree (Kadi Patta)": 68.0,
        "Jackfruit": 220.0,
        "Coconut Palm": 245.0,
        "Neem (Outdoor)": 135.6,
        "Bamboo": 280.0,
        "Rain Tree (Samanea)": 195.0,
        "Gulmohar (Flame Tree)": 95.2,
        "Jacaranda": 112.0,
        "Bakul (Mimusops)": 105.0,

        # BALCONY/INDOOR PLANTS (Lower but still significant)
        "Snake Plant (Sansevieria)": 18.0,
        "Tulsi (Holy Basil)": 15.0,
        "Money Plant (Pothos)": 22.0,
        "Aloe Vera": 12.0,
        "Mint (Pudina)": 8.0,
        "Spider Plant": 20.0,
        "Coriander (Dhania)": 5.0,
        "Peace Lily": 25.0,
        "Tomato (Dwarf Variety)": 10.0,
        "Areca Palm": 30.0,
        "Curry Leaves (Kadi Patta)": 16.0,
        "Jade Plant": 11.0,
        "Rubber Plant": 35.0,
        "Boston Fern": 28.0,

        # MEDICINAL PLANTS
        "Lavender": 9.0,
        "Rosemary": 10.0,
        "Brahmi (Bacopa)": 7.0,
        "Ashwagandha (Indian Ginseng)": 13.0,
        "Stevia (Sweet Leaf)": 8.0,
        "Lemongrass (Hari Chai Patti)": 14.0,
        "Ajwain (Carom Plant)": 6.0,
        "Methi (Fenugreek)": 5.0,
        "Ginger (Adrak)": 11.0,
        "Turmeric (Haldi)": 12.0,
        "Insulin Plant (Costus)": 15.0,
        "Hibiscus (Gudhal)": 26.0,
        "English Ivy": 24.0,
    }

    # Return value for the tree or default value if not found
    return pollutant_values.get(tree_name, 50.0)


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