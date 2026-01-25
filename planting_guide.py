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
        # EXISTING OUTDOOR TREES (keep these)
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
        ],

        # NEW: BALCONY PLANTS (15 total)
        "Snake Plant (Sansevieria)": [
            "Choose a pot with drainage holes (6-8 inches diameter)",
            "Fill with well-draining cactus/succulent mix",
            "Plant at same depth as nursery pot",
            "Water once every 2-3 weeks (let soil dry completely)",
            "Place in any location - tolerates low light well",
            "Fertilize once every 2-3 months with diluted liquid fertilizer"
        ],
        "Tulsi (Holy Basil)": [
            "Select 8-10 inch pot with good drainage",
            "Use soil mix: 40% garden soil + 30% cocopeat + 30% compost",
            "Plant seeds 1cm deep or transplant seedling carefully",
            "Water daily in morning (keep soil moist but not waterlogged)",
            "Place in location with 6+ hours direct sunlight",
            "Pinch growing tips regularly to encourage bushiness",
            "Harvest leaves from top to promote new growth"
        ],
        "Money Plant (Pothos)": [
            "Use 6-8 inch pot with drainage holes",
            "Plant in regular potting mix or even water (hydroponic)",
            "Keep 2-3 nodes below soil if planting cutting",
            "Water when top inch of soil feels dry (twice weekly)",
            "Grows well in indirect bright light",
            "Can be grown as climber (provide support) or trailing plant",
            "Wipe leaves monthly to remove dust"
        ],
        "Aloe Vera": [
            "Choose 8-10 inch terracotta pot (porous, aids drainage)",
            "Use cactus/succulent soil mix or add sand to regular soil",
            "Plant so that lower leaves are just above soil line",
            "Water deeply but infrequently (every 2 weeks)",
            "Place in bright location with 6+ hours sunlight",
            "Avoid overwatering - leads to root rot",
            "Harvest outer leaves when plant is mature (2+ years)"
        ],
        "Mint (Pudina)": [
            "Use 8-10 inch wide pot (mint spreads horizontally)",
            "Fill with well-draining potting mix rich in compost",
            "Plant stem cuttings 2-3 inches deep",
            "Water daily to keep soil consistently moist",
            "Provide 4-6 hours sunlight (partial shade acceptable)",
            "Harvest leaves regularly to prevent flowering",
            "Divide and repot every 6 months to control spread"
        ],
        "Spider Plant": [
            "Select 6-8 inch pot with drainage",
            "Use standard potting mix",
            "Plant so crown is at soil level (not buried)",
            "Water 2-3 times weekly (when top inch is dry)",
            "Grows well in indirect light",
            "Produces baby plants (spiderettes) - can be propagated",
            "Remove brown tips by trimming with scissors"
        ],
        "Coriander (Dhania)": [
            "Use 8-10 inch pot, at least 6 inches deep",
            "Fill with loose, well-draining potting mix",
            "Sow seeds 1/4 inch deep, 2 inches apart",
            "Water daily lightly (keep soil moist)",
            "Provide 4-6 hours sunlight",
            "Germination occurs in 7-10 days",
            "Harvest leaves when plant is 6 inches tall",
            "Replant every 3-4 weeks for continuous harvest"
        ],
        "Peace Lily": [
            "Choose 8-10 inch pot with drainage",
            "Use rich, well-draining potting mix with peat moss",
            "Plant at same depth as original container",
            "Water weekly (when top inch is dry)",
            "Thrives in low to medium indirect light",
            "Mist leaves weekly to increase humidity",
            "Remove spent flowers and yellow leaves promptly"
        ],
        "Tomato (Dwarf Variety)": [
            "Use large 12-14 inch pot (5-gallon capacity minimum)",
            "Fill with nutrient-rich potting mix + compost",
            "Plant seedling deep (up to first set of leaves)",
            "Water daily in morning (needs consistent moisture)",
            "Requires 6-8 hours direct sunlight",
            "Provide stake or cage support as plant grows",
            "Fertilize every 2 weeks with tomato-specific fertilizer",
            "Pinch off suckers between main stem and branches"
        ],
        "Areca Palm": [
            "Select large 14-16 inch pot with drainage",
            "Use well-draining potting mix with peat and perlite",
            "Plant at same depth as nursery pot",
            "Water 3 times weekly (keep soil slightly moist)",
            "Provide bright, indirect light (4-6 hours)",
            "Mist leaves regularly to maintain humidity",
            "Fertilize monthly during growing season",
            "Remove yellow fronds at base"
        ],
        "Curry Leaves (Kadi Patta)": [
            "Use 12-14 inch pot with good drainage",
            "Plant in mix: 50% garden soil + 30% compost + 20% sand",
            "Plant seedling or stem cutting 3-4 inches deep",
            "Water daily (keep soil consistently moist)",
            "Requires 6-8 hours direct sunlight",
            "Fertilize monthly with organic fertilizer",
            "Prune regularly to encourage branching",
            "Protect from frost in winter"
        ],
        "Jade Plant": [
            "Choose small 6-8 inch pot with drainage holes",
            "Use cactus/succulent soil mix",
            "Plant cutting or small plant at soil level",
            "Water every 2 weeks (let soil dry completely)",
            "Provide 4-6 hours sunlight",
            "Very low maintenance - avoid overwatering",
            "Fertilize once every 3-4 months"
        ],
        # NEW OUTDOOR TREES
        "Jackfruit (Kathal)": [
            "Requires large space - plant at least 25-30 feet from structures",
            "Dig hole 3 feet deep and wide, fill with compost-enriched soil",
            "Plant grafted saplings for fruit in 3-4 years (seedlings take 7-8 years)",
            "Water regularly in first 2 years, then tree is self-sufficient",
            "Stake heavily - young jackfruit trees need support",
            "Apply organic manure twice yearly (spring and monsoon)"
        ],
        "Coconut (Nariyal)": [
            "Best suited for coastal or warm, humid regions",
            "Dig hole 3x3 feet, add 20kg compost and cocopeat mix",
            "Place germinated nut horizontally, 1/3rd above soil",
            "Water daily for first 3 years (coconuts need consistent moisture)",
            "Apply 50kg organic manure + 2kg salt annually",
            "Mulch heavily to retain moisture around base"
        ],
        "Tamarind (Imli)": [
            "Choose permanent location - tamarind trees are long-lived (150+ years)",
            "Very deep roots - avoid planting near buildings or pipes",
            "Requires minimal care once established (extremely hardy)",
            "Water only in extreme drought during first 2 years",
            "No fertilizer needed - tamarind thrives in poor soil",
            "Prune lower branches for easier fruit collection"
        ],
        "Karanj (Pongamia)": [
            "Salt-tolerant - excellent for coastal erosion control",
            "Can grow in poor, degraded soil (nitrogen-fixing roots)",
            "Water moderately in first year, then rain-fed",
            "Survives flooding and waterlogging",
            "Space 15-20 feet apart in plantations",
            "Seeds used for biodiesel - harvest after 4-5 years"
        ],
        "Kadamba": [
            "Prefers moist, well-drained soil near water bodies",
            "Fast-growing - needs ample space (40 feet spread)",
            "Water generously in first 2 years",
            "Apply compost in monsoon season",
            "Pruning not required - natural rounded canopy",
            "Flowers attract butterflies and bees"
        ],
        "Parijat (Night Jasmine)": [
            "Can be grown as small tree or large shrub",
            "Prefers partial shade in hot regions",
            "Use well-draining soil mix with compost",
            "Water regularly but avoid waterlogging",
            "Flowers bloom at night and fall by morning",
            "Collect fallen flowers for tea or worship use"
        ],
        "Bael (Wood Apple)": [
            "Extremely hardy - survives neglect and drought",
            "Plant in full sun for best fruiting",
            "Deep taproot - difficult to transplant after establishment",
            "Minimal watering needed after first year",
            "Thorny branches - handle carefully during pruning",
            "Fruits ripen in 10-11 months (harvest when yellow)"
        ],
        "Custard Apple (Sitaphal)": [
            "Prefers dry climate with distinct wet and dry seasons",
            "Plant in raised beds if soil drainage is poor",
            "Water regularly during flowering and fruiting",
            "Prune to maintain manageable height (8-10 feet)",
            "Apply potash-rich fertilizer before flowering",
            "Fruits mature in 4-5 months after flowering"
        ],

        # NEW BALCONY PLANTS
        "Basil (Sweet Basil)": [
            "Use 8-10 inch pot with drainage holes",
            "Plant in nutrient-rich potting mix",
            "Sow seeds 1/4 inch deep or transplant seedlings",
            "Water daily to keep soil moist (not soggy)",
            "Pinch off flower buds to encourage leaf growth",
            "Harvest leaves from top to promote bushiness",
            "Replant every 3-4 months for fresh supply"
        ],
        "Rosemary": [
            "Use well-draining cactus/succulent mix",
            "Plant in terracotta pot (breathable)",
            "Avoid overwatering - let top inch dry between watering",
            "Requires at least 6 hours direct sunlight",
            "Prune regularly to prevent legginess",
            "Can survive indoors near bright window",
            "Drought-tolerant once established"
        ],
        "Chili Pepper (Dwarf)": [
            "Use 10-12 inch deep pot with drainage",
            "Plant in nutrient-rich mix with compost",
            "Transplant seedlings after 4-6 weeks",
            "Water daily during fruiting stage",
            "Provide stake support as plant grows",
            "Fertilize every 2 weeks with balanced NPK",
            "Harvest chillies when fully colored"
        ],
        "Oregano": [
            "Use 8-10 inch pot with excellent drainage",
            "Plant in well-draining potting mix",
            "Water only when top inch is dry (avoid overwatering)",
            "Prefers full sun but tolerates partial shade",
            "Pinch growing tips to encourage bushy growth",
            "Harvest leaves before flowering for best flavor",
            "Very drought-tolerant - ideal for beginners"
        ],
        "Thyme": [
            "Use shallow 6-8 inch pot (thyme has shallow roots)",
            "Plant in sandy, well-draining mix",
            "Water sparingly - thyme prefers dry conditions",
            "Requires full sun (6+ hours)",
            "Trim regularly to prevent woody growth",
            "Harvest sprigs as needed (leaves most flavorful before flowering)",
            "Extremely low maintenance"
        ],
        "ZZ Plant": [
            "Use pot with drainage holes (6-10 inches)",
            "Plant in well-draining potting mix",
            "Water only when soil is completely dry (every 2-3 weeks)",
            "Tolerates low light but grows faster in bright indirect light",
            "Wipe leaves monthly to remove dust",
            "Virtually indestructible - perfect for beginners",
            "Toxic if ingested - keep away from pets and children"
        ],
        "Golden Pothos": [
            "Use 6-8 inch pot or hanging basket",
            "Plant in regular potting mix or water (hydroponic)",
            "Water when top 2 inches are dry",
            "Thrives in low to bright indirect light",
            "Prune regularly to control length",
            "Propagate easily from stem cuttings in water",
            "Variegation fades in very low light"
        ],
        "Weeping Fig": [
            "Use large 12-16 inch pot with drainage",
            "Plant in well-draining potting mix",
            "Water when top 2 inches dry (2-3 times weekly)",
            "Needs bright, indirect light (not direct sun)",
            "Sensitive to location changes - avoid moving once established",
            "Mist leaves weekly to increase humidity",
            "Drops leaves when stressed (normal adjustment response)"
        ],
        "Croton": [
            "Use 10-14 inch pot with drainage",
            "Plant in rich, well-draining potting mix",
            "Keep soil consistently moist (water 3-4 times weekly)",
            "Requires bright light for vibrant colors (6+ hours)",
            "Mist regularly - prefers high humidity",
            "Wipe leaves weekly to showcase colors",
            "Toxic to pets - keep out of reach"
        ],
        "English Ivy": [
            "Use 6-8 inch pot or hanging basket",
            "Plant in moisture-retaining potting mix",
            "Water frequently to keep soil consistently moist",
            "Grows well in low to medium light",
            "Excellent air purifier - removes mold spores",
            "Prune to control growth and shape",
            "Toxic to pets - keep away from cats and dogs"
        ],
        "Brahmi (Indian Pennywort)": [
            "Use wide, shallow pot (8-10 inches) - Brahmi spreads horizontally",
            "Plant in rich, moist potting mix with compost",
            "Keep soil consistently wet (can even grow in water tray)",
            "Prefers partial shade in hot climates",
            "Pinch growing tips to encourage dense growth",
            "Harvest leaves regularly to promote new growth",
            "Can propagate easily from stem cuttings in water",
            "MEDICINAL USE: Chew 4-5 fresh leaves every morning for memory and focus"
        ],
        "Ashwagandha (Indian Ginseng)": [
            "Use deep pot (12-14 inches) for taproot development",
            "Plant in well-draining sandy-loamy mix",
            "Sow seeds ½ inch deep OR transplant seedlings",
            "Water sparingly - prefers dry conditions (every 2-3 days)",
            "Requires full sun (6+ hours)",
            "Harvest roots after 6-8 months (when leaves yellow)",
            "Dry roots in shade, grind to powder and store",
            "MEDICINAL USE: ½ tsp root powder in warm milk before bed"
        ],
        "Stevia (Sweet Leaf)": [
            "Use 10-12 inch pot with good drainage",
            "Plant in rich, slightly acidic potting mix",
            "Keep soil consistently moist (not waterlogged)",
            "Provide 5-7 hours sunlight",
            "Pinch tips regularly to prevent flowering (leaves lose sweetness)",
            "Harvest leaves when plant is 8-10 inches tall",
            "Dry leaves in shade, store in airtight container",
            "MEDICINAL USE: 1 fresh leaf = 1 tsp sugar (300x sweeter!)"
        ],
        "Lemongrass (Hari Chai Patti)": [
            "Use large pot (12-14 inches) as lemongrass spreads",
            "Plant in well-draining potting mix",
            "Buy a stalk from market, place in water until roots appear",
            "Transplant to pot once roots are 2-3 inches",
            "Water daily - keeps soil moist",
            "Requires full sun (6+ hours)",
            "Harvest outer stalks when 12+ inches tall",
            "MEDICINAL USE: Crush 2-3 stalks, boil for tea to cure indigestion"
        ],
        "Ajwain (Carom Plant)": [
            "Use 10-12 inch pot with excellent drainage",
            "Plant in light, sandy potting mix",
            "Sow seeds ¼ inch deep",
            "Water every 2 days (avoid overwatering)",
            "Needs 5-7 hours sunlight",
            "Pinch growing tips to encourage bushy growth",
            "Harvest seeds when they turn brown (4-5 months)",
            "MEDICINAL USE: Chew ½ tsp seeds after heavy meals for instant gas relief"
        ],
        "Methi (Fenugreek)": [
            "Use 8-10 inch pot, shallow is fine",
            "Scatter seeds densely (microgreens style)",
            "Cover with ¼ inch soil, water gently",
            "Keep soil moist, germination in 3-5 days",
            "Harvest as microgreens (7-10 days) OR let mature (30 days)",
            "For seeds, wait 3-4 months",
            "Resow every 2-3 weeks for continuous supply",
            "MEDICINAL USE: Soak 1 tbsp seeds overnight, drink water on empty stomach for diabetes"
        ],
        "Ginger (Adrak)": [
            "Buy fresh ginger rhizome with 'eyes' (growth buds)",
            "Use wide, shallow pot (12-14 inches, 8 inches deep)",
            "Plant rhizome 2 inches deep, buds facing up",
            "Use rich, well-draining potting mix with compost",
            "Keep soil consistently moist (not soggy)",
            "Prefers partial shade (4-6 hours indirect light)",
            "Harvest after 8-10 months when leaves yellow",
            "MEDICINAL USE: Grate fresh ginger, boil with tulsi for cold/cough relief"
        ],
        "Turmeric (Haldi)": [
            "Buy fresh turmeric rhizome from market",
            "Use large, deep pot (14-16 inches)",
            "Plant 2-3 inches deep in rich potting mix",
            "Water daily to keep soil moist",
            "Prefers warm, humid conditions",
            "Partial shade is ideal (4-6 hours)",
            "Harvest after 8-10 months (when leaves dry)",
            "Boil, dry, and grind into powder",
            "MEDICINAL USE: Turmeric milk (haldi doodh) every night for immunity"
        ],
        "Insulin Plant (Costus)": [
            "Use 10-12 inch pot with drainage holes",
            "Plant in well-draining potting mix with compost",
            "Keep soil moist but not waterlogged",
            "Prefers partial shade (4-6 hours indirect light)",
            "Mist leaves regularly (likes humidity)",
            "Very low maintenance once established",
            "Propagates easily from stem cuttings",
            "MEDICINAL USE: Chew 1-2 leaves on empty stomach daily (proven to reduce blood sugar)"
        ],
        "Hibiscus (Gudhal)": [
            "Use large pot (14-16 inches) for shrub growth",
            "Plant in nutrient-rich potting mix",
            "Water daily - hibiscus loves moisture",
            "Requires full sun (6+ hours) for flowering",
            "Fertilize every 2 weeks during growing season",
            "Prune regularly to maintain shape and promote flowering",
            "Deadhead spent flowers to encourage more blooms",
            "MEDICINAL USE: Grind 5-6 leaves + 2 flowers into paste, apply to hair for 30 mins (stops hairfall)"
        ],


        "Rubber Plant": [
            "Select 12-16 inch pot with drainage",
            "Use well-draining potting mix",
            "Plant at same depth as nursery container",
            "Water twice weekly (when top 2 inches dry)",
            "Needs bright, indirect light (4-6 hours)",
            "Wipe leaves weekly with damp cloth",
            "Prune to control size and shape",
            "Fertilize monthly during spring and summer"
        ],
        "Boston Fern": [
            "Use 10-12 inch pot or hanging basket",
            "Fill with peat-based potting mix (retains moisture)",
            "Plant so crown is slightly above soil",
            "Water 3-4 times weekly (keep consistently moist)",
            "Prefers high humidity - mist daily or use pebble tray",
            "Grows well in indirect light (2-4 hours)",
            "Remove brown fronds regularly",
            "Avoid placing near heating vents or AC"
        ]
    }
    
    # Combine common steps with specific steps (if available)
    if tree_name in specific_steps:
        return specific_steps[tree_name]
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
