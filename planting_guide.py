def get_planting_guide(tree_name):
    """
    Provides step-by-step planting instructions for a specific tree species.
    
    Args:
        tree_name (str): Name of the tree species
        
    Returns:
        list: Steps for planting the tree
    """
    # Common planting steps for all trees
    common_steps = [
        "Choose a location that matches the tree's sunlight, space, and soil requirements.",
        "Dig a hole 2-3 times wider than the root ball and as deep as the root ball height.",
        "Gently remove the tree from its container, being careful not to damage the roots.",
        "Place the tree in the hole, ensuring that it stands straight and the top of the root ball is level with or slightly above the ground.",
        "Backfill the hole with soil, firmly but gently packing it to eliminate air pockets.",
        "Create a water basin around the tree by building a circular ridge of soil.",
        "Water thoroughly after planting until the soil is well-moistened.",
        "Apply a 5-10 cm layer of mulch around the base, keeping it away from the trunk.",
        "Stake the tree if needed, especially in windy areas."
    ]
    
    # Tree-specific additional steps
    specific_steps = {
        "Neem": [
            "Neem prefers well-drained soil, so ensure good drainage if your soil is clay-heavy.",
            "Space multiple neem trees at least 8-10 meters apart to allow for their full canopy spread."
        ],
        "Banyan": [
            "Choose a location with ample space, as banyan trees develop extensive root systems and wide canopies.",
            "Avoid planting near buildings or infrastructure due to the invasive nature of its roots."
        ],
        "Arjuna": [
            "Arjuna trees prefer moist soil and do well near water bodies.",
            "Ensure the soil has good organic content by mixing compost during planting."
        ],
        "Peepal": [
            "Plant away from structures as peepal roots can be invasive.",
            "Choose a permanent location as peepal trees are considered sacred and should not be relocated."
        ],
        "Gulmohar": [
            "Plant in an open area to accommodate its wide, spreading canopy.",
            "Ensure the planting site has good drainage as gulmohar doesn't tolerate waterlogging."
        ],
        "Ashoka": [
            "Ashoka trees prefer partial shade during their early growth years.",
            "Ensure regular watering during the establishment period as they prefer consistent moisture."
        ],
        "Mango": [
            "Plant in a location protected from strong winds.",
            "If planting for fruit production, consider grafted varieties over seedlings.",
            "Apply organic fertilizer during planting to support healthy fruit development."
        ],
        "Amaltas": [
            "Choose a sunny location for the best flowering.",
            "Ensure good drainage as amaltas is susceptible to root rot in waterlogged conditions."
        ],
        "Jamun": [
            "Plant in deep, loamy soil for best growth and fruit production.",
            "Space trees at least 10 meters apart to allow for their full development."
        ],
        "Amla": [
            "Amla can tolerate poor soil conditions but performs best in well-drained, fertile soil.",
            "Apply organic manure during planting to improve fruit yield."
        ],
        "Silver Oak": [
            "Silver oak grows rapidly, so consider its mature height and spread when selecting a location.",
            "Use a slow-release fertilizer at planting time to support its fast growth rate."
        ],
        "Eucalyptus": [
            "Plant away from water sources and agricultural fields as eucalyptus can deplete groundwater.",
            "Space trees at least 5-6 meters apart if planting in rows for windbreaks."
        ]
    }
    
    # Combine common steps with specific steps (if available)
    if tree_name in specific_steps:
        return common_steps + specific_steps[tree_name]
    else:
        return common_steps

def get_maintenance_guide(tree_name):
    """
    Provides seasonal maintenance instructions for a specific tree species.
    
    Args:
        tree_name (str): Name of the tree species
        
    Returns:
        dict: Seasonal maintenance guides
    """
    # Common maintenance tasks for all trees
    common_maintenance = {
        "Spring": [
            "Check for new growth and signs of pests or diseases.",
            "Apply a balanced fertilizer before the growing season starts.",
            "Remove any damaged branches from winter."
        ],
        "Summer": [
            "Water deeply during dry periods, especially for young trees.",
            "Monitor for pest infestations and treat as necessary.",
            "Maintain mulch layer to conserve moisture and suppress weeds."
        ],
        "Monsoon": [
            "Check soil drainage and adjust if water is pooling around the tree.",
            "Watch for fungal diseases which are more common in humid conditions.",
            "Support the tree with stakes if heavy rains have loosened the soil."
        ],
        "Winter": [
            "Reduce watering as growth slows down.",
            "Protect young trees from frost if in a cold region.",
            "Prune dead or diseased branches during the dormant season."
        ]
    }
    
    # Tree-specific seasonal maintenance
    specific_maintenance = {
        "Neem": {
            "Spring": [
                "Apply neem cake as organic fertilizer around the base.",
                "Prune to maintain shape if needed."
            ],
            "Summer": [
                "Minimal watering required as neem is drought-tolerant."
            ],
            "Monsoon": [
                "Check for termite infestations at the base of the trunk."
            ]
        },
        "Banyan": {
            "Spring": [
                "Remove any aerial roots that may be growing toward unwanted areas."
            ],
            "Summer": [
                "Young banyan trees need regular watering for the first few years."
            ],
            "Winter": [
                "Prune cautiously, focusing only on damaged branches."
            ]
        },
        "Mango": {
            "Spring": [
                "Apply potassium-rich fertilizer before flowering.",
                "Watch for mango hoppers and treat if present."
            ],
            "Summer": [
                "Water regularly during fruit development.",
                "Protect developing fruit from birds and bats if necessary."
            ],
            "Winter": [
                "Prune after harvest to maintain tree size and shape.",
                "Apply organic manure in late winter."
            ]
        },
        "Eucalyptus": {
            "Spring": [
                "Minimal maintenance required.",
                "Check for and remove any competing vegetation."
            ],
            "Summer": [
                "Generally drought-resistant but water young trees in extreme heat."
            ],
            "Winter": [
                "No special care needed as eucalyptus is cold-hardy in most Indian regions."
            ]
        }
    }
    
    # Combine common maintenance with specific maintenance
    maintenance_guide = common_maintenance.copy()
    
    if tree_name in specific_maintenance:
        for season, tasks in specific_maintenance[tree_name].items():
            if season in maintenance_guide:
                maintenance_guide[season].extend(tasks)
    
    return maintenance_guide
