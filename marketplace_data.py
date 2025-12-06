"""
Marketplace Data Module
Provides product data for the AirCare marketplace
"""


def get_marketplace_products():
    """
    Returns list of all marketplace products

    Returns:
        list: List of product dictionaries with keys:
            - name (str): Product name
            - category (str): Product category
            - price (int): Price in INR
            - description (str): Product description
            - benefits (str): Product benefits/features
    """

    products = [
        # =====================================
        # CATEGORY: SEEDS
        # =====================================
        {
            'name': 'Neem Seeds (50g)',
            'category': 'Seeds',
            'price': 150,
            'description': 'Organic neem seeds for planting. Excellent for outdoor gardens.',
            'benefits': 'Natural pest repellent, medicinal properties, fast-growing tree'
        },
        {
            'name': 'Tulsi Seeds (Holy Basil)',
            'category': 'Seeds',
            'price': 80,
            'description': 'Pack of 50+ Tulsi seeds. Perfect for balcony gardens.',
            'benefits': 'Medicinal plant, air purification, religious significance'
        },
        {
            'name': 'Tomato Seeds (Dwarf Variety)',
            'category': 'Seeds',
            'price': 120,
            'description': 'Hybrid dwarf tomato seeds ideal for balcony cultivation.',
            'benefits': 'Fresh vegetables at home, compact growth, high yield'
        },
        {
            'name': 'Coriander Seeds (100g)',
            'category': 'Seeds',
            'price': 60,
            'description': 'Premium quality coriander seeds for quick germination.',
            'benefits': 'Fast growing, continuous harvest, culinary herb'
        },
        {
            'name': 'Coriander Seeds (100g)',
            'category': 'Seeds',
            'price': 60,
            'description': 'Premium quality coriander seeds for quick germination.',
            'benefits': 'Fast growing, continuous harvest, culinary herb'
        },
        {
            'name': 'Mint Seeds',
            'category': 'Seeds',
            'price': 70,
            'description': 'Organic mint seeds. Grows rapidly in any condition.',
            'benefits': 'Aromatic herb, easy to grow, medicinal uses'
        },
        {
            'name': 'Curry Leaf Seeds',
            'category': 'Seeds',
            'price': 200,
            'description': 'Authentic curry leaf tree seeds. Takes 6-8 months to grow.',
            'benefits': 'Essential Indian herb, medicinal properties, aromatic'
        },

        # =====================================
        # CATEGORY: POTS & CONTAINERS
        # =====================================
        {
            'name': 'Terracotta Pot (8 inch)',
            'category': 'Pots',
            'price': 120,
            'description': 'Traditional clay pot with drainage hole. Perfect for herbs.',
            'benefits': 'Breathable, natural cooling, prevents overwatering'
        },
        {
            'name': 'Plastic Planter (10 inch)',
            'category': 'Pots',
            'price': 80,
            'description': 'Lightweight plastic pot with saucer. Available in multiple colors.',
            'benefits': 'Lightweight, affordable, retains moisture well'
        },
        {
            'name': 'Hanging Pot Set (3 pcs)',
            'category': 'Pots',
            'price': 450,
            'description': 'Set of 3 hanging pots with metal chains. Ideal for balconies.',
            'benefits': 'Space-saving, decorative, perfect for trailing plants'
        },
        {
            'name': 'Grow Bags (5 pack)',
            'category': 'Pots',
            'price': 250,
            'description': 'Fabric grow bags (12x12 inch). Reusable and portable.',
            'benefits': 'Excellent drainage, air pruning, lightweight, eco-friendly'
        },
        {
            'name': 'Ceramic Decorative Pot',
            'category': 'Pots',
            'price': 350,
            'description': 'Hand-painted ceramic pot (6 inch). Premium quality.',
            'benefits': 'Aesthetic appeal, durable, perfect for indoor plants'
        },
        {
            'name': 'Vertical Planter (5 tier)',
            'category': 'Pots',
            'price': 1200,
            'description': 'Space-saving vertical planter. Ideal for herbs and small plants.',
            'benefits': 'Maximizes space, modern design, holds 10-15 plants'
        },

        # =====================================
        # CATEGORY: SOIL & FERTILIZER
        # =====================================
        {
            'name': 'Organic Potting Mix (5 kg)',
            'category': 'Soil & Fertilizer',
            'price': 200,
            'description': 'Ready-to-use potting mix with cocopeat, compost, and perlite.',
            'benefits': 'Well-draining, nutrient-rich, suitable for all plants'
        },
        {
            'name': 'Vermicompost (2 kg)',
            'category': 'Soil & Fertilizer',
            'price': 150,
            'description': 'Premium quality worm compost. 100% organic.',
            'benefits': 'Rich in nutrients, improves soil structure, eco-friendly'
        },
        {
            'name': 'Neem Cake Fertilizer (1 kg)',
            'category': 'Soil & Fertilizer',
            'price': 180,
            'description': 'Organic neem cake powder. Acts as fertilizer and pest repellent.',
            'benefits': 'Dual purpose, organic, slow-release nutrients'
        },
        {
            'name': 'NPK Fertilizer (500g)',
            'category': 'Soil & Fertilizer',
            'price': 120,
            'description': 'Balanced NPK 19:19:19 fertilizer for all-purpose use.',
            'benefits': 'Fast-acting, promotes growth, flowers, and fruits'
        },
        {
            'name': 'Cocopeat Block (650g)',
            'category': 'Soil & Fertilizer',
            'price': 90,
            'description': 'Compressed cocopeat block. Expands to 5kg when soaked.',
            'benefits': 'Excellent water retention, eco-friendly, reusable'
        },
        {
            'name': 'Bone Meal Fertilizer (1 kg)',
            'category': 'Soil & Fertilizer',
            'price': 160,
            'description': 'Organic phosphorus-rich fertilizer for flowering plants.',
            'benefits': 'Promotes root growth, flowering, and fruiting'
        },

        # =====================================
        # CATEGORY: TOOLS & ACCESSORIES
        # =====================================
        {
            'name': 'Gardening Tool Kit (5 pieces)',
            'category': 'Tools',
            'price': 350,
            'description': 'Essential tool set: trowel, rake, pruner, gloves, spray bottle.',
            'benefits': 'Complete starter kit, durable, ergonomic design'
        },
        {
            'name': 'Watering Can (2 Liter)',
            'category': 'Tools',
            'price': 180,
            'description': 'Plastic watering can with long spout for precision watering.',
            'benefits': 'Easy to use, precise watering, prevents soil erosion'
        },
        {
            'name': 'Pruning Shears',
            'category': 'Tools',
            'price': 250,
            'description': 'Professional-grade pruning scissors with safety lock.',
            'benefits': 'Sharp blades, comfortable grip, long-lasting'
        },
        {
            'name': 'Plant Mister Spray Bottle',
            'category': 'Tools',
            'price': 120,
            'description': 'Fine mist spray bottle (500ml) for foliar feeding and humidity.',
            'benefits': 'Increases humidity, cleans leaves, applies liquid fertilizer'
        },
        {
            'name': 'Soil pH Meter',
            'category': 'Tools',
            'price': 400,
            'description': 'Digital pH and moisture meter. No batteries required.',
            'benefits': 'Accurate readings, helps optimize plant health'
        },
        {
            'name': 'Plant Support Stakes (10 pack)',
            'category': 'Tools',
            'price': 150,
            'description': 'Bamboo stakes (24 inch) for supporting climbing plants.',
            'benefits': 'Natural, sturdy, biodegradable'
        },

        # =====================================
        # CATEGORY: AIR QUALITY PRODUCTS
        # =====================================
        {
            'name': 'Air Quality Monitor',
            'category': 'Air Quality',
            'price': 2500,
            'description': 'Digital AQI monitor. Measures PM2.5, PM10, temperature, humidity.',
            'benefits': 'Real-time monitoring, accurate sensors, portable'
        },
        {
            'name': 'HEPA Air Purifier (Small Room)',
            'category': 'Air Quality',
            'price': 5500,
            'description': 'Compact HEPA air purifier for rooms up to 200 sq ft.',
            'benefits': 'Removes 99.97% pollutants, quiet operation, low power'
        },
        {
            'name': 'Activated Charcoal Air Purifier Bags',
            'category': 'Air Quality',
            'price': 350,
            'description': 'Set of 4 bamboo charcoal bags. Natural odor eliminator.',
            'benefits': 'Chemical-free, reusable for 2 years, eco-friendly'
        },
        {
            'name': 'Indoor Plant Bundle (5 plants)',
            'category': 'Air Quality',
            'price': 1200,
            'description': 'Starter pack: Snake Plant, Money Plant, Spider Plant, Aloe, Peace Lily.',
            'benefits': 'NASA-approved air purifiers, low maintenance, variety'
        },
        {
            'name': 'Himalayan Salt Lamp',
            'category': 'Air Quality',
            'price': 800,
            'description': 'Natural salt crystal lamp. Creates negative ions.',
            'benefits': 'Improves air quality, ambient lighting, reduces allergens'
        },
        {
            'name': 'Essential Oil Diffuser',
            'category': 'Air Quality',
            'price': 1100,
            'description': 'Ultrasonic aroma diffuser with LED lights. 300ml capacity.',
            'benefits': 'Aromatherapy, humidifies air, stress relief'
        }
    ]

    return products