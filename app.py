import streamlit as st
import pandas as pd
from community import initialize_community, display_community_feed
import geopy
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import datetime
import uuid

# Import custom modules
from tree_data import get_tree_data, get_tree_details, get_balcony_plants_data
from recommendation import get_recommendations, get_balcony_recommendations
from climate_data import get_climate_data
from soil_data import get_soil_types, get_soil_data
from impact_calculator import calculate_impact
from utils import display_tree_svg
from planting_guide import get_planting_guide, get_maintenance_guide
from user_profile import (
    initialize_user_profile,
    add_xp,
    calculate_green_score,
    display_profile_sidebar,
    update_streak,
    check_and_award_badges
)

# Set page configuration
st.set_page_config(
    page_title="Tree Plantation Planner",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ----------------------
# Initialize session state
# ----------------------
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'location': None,
        'climate_data': None,
        'soil_data': None,
        'recommended_trees': None,
        'selected_tree': None,
        'planted_trees': [],
        'is_balcony_mode': False,
        'space_size': 'Small (0.5-2 m²)',
        'sunlight_hours': 6,
        'planting_purpose': [],
        'balcony_direction': 'East',
        'current_page': 'Home',
        'watering_logs': {},  # NEW: {plant_id: [dates]}
        'plant_photos': {},  # NEW: {plant_id: [photo_data]}
        'care_reminders': {}  # NEW: {plant_id: reminder_data}
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()

# Initialize user profile and community only once
if 'user_profile' not in st.session_state:
    initialize_user_profile()
    initialize_community()
    update_streak()


# ----------------------
# FIXED NAVIGATION SYSTEM
# ----------------------
def navigate_to(page_name):
    """Centralized navigation function"""
    st.session_state.current_page = page_name
    st.rerun()


# Check for programmatic navigation request
if 'navigate_to' in st.session_state and st.session_state.navigate_to:
    st.session_state.current_page = st.session_state.navigate_to
    st.session_state.navigate_to = None

# ----------------------
# FIXED LOCATION SYSTEM
# ----------------------
query_params = st.query_params

# Handle geolocation from browser
if "lat" in query_params and "lon" in query_params:
    try:
        lat = float(query_params["lat"])
        lon = float(query_params["lon"])

        # Reverse geocode to get address
        geolocator = Nominatim(user_agent="tree_planner")
        location = geolocator.reverse(f"{lat}, {lon}")

        st.session_state.location = {
            "address": location.address if location else f"Lat: {lat}, Lon: {lon}",
            "latitude": lat,
            "longitude": lon
        }

        # Fetch climate & soil data
        st.session_state.climate_data = get_climate_data(lat, lon)
        st.session_state.soil_data = get_soil_data(lat, lon)

        # Generate recommendations
        if st.session_state.is_balcony_mode:
            st.session_state.recommended_trees = get_balcony_recommendations(
                st.session_state.space_size,
                st.session_state.sunlight_hours,
                st.session_state.planting_purpose,
                st.session_state.climate_data
            )
        else:
            st.session_state.recommended_trees = get_recommendations(
                st.session_state.climate_data,
                st.session_state.soil_data
            )

        # Clear params and navigate
        st.query_params.clear()
        st.session_state.current_page = "Tree Recommendations"
        st.rerun()

    except Exception as e:
        st.error(f"Error processing location: {e}")

# ----------------------
# Sidebar Navigation (READ ONLY - doesn't control page)
# ----------------------
page_options = ["Home", "Tree Recommendations", "Planting Guide", "Plant Care Tracker", "Impact Tracker", "Community",
                "About"]

# Display current page in sidebar
with st.sidebar:
    st.markdown(f"### 📍 Current Page: **{st.session_state.current_page}**")
    st.markdown("---")

    # Navigation buttons (replaces radio)
    for page in page_options:
        if st.button(page, key=f"nav_{page}", use_container_width=True):
            navigate_to(page)

# Display user profile in sidebar
display_profile_sidebar()
display_tree_svg()


# ----------------------
# Utility Functions
# ----------------------
def ensure_tree_has_fields(tree):
    """Ensure tree object has all required fields"""
    defaults = {
        'id': str(uuid.uuid4()),
        'status': 'Newly Planted',
        'health': 'Good',
        'planted_date': datetime.datetime.now().strftime("%Y-%m-%d"),
        'name': 'Unknown Plant',
        'purposes': [],
        'environmental_benefits': 'N/A',
        'benefits': 'N/A'
    }

    for key, default_value in defaults.items():
        if key not in tree:
            tree[key] = default_value

    return tree


# ----------------------
# App Title
# ----------------------
st.title("🌳 Tree Plantation Planner")
st.markdown("""
A data-driven approach to planting the right trees in the right places.
""")

# ----------------------
# PAGES
# ----------------------

# ===========================
# HOME PAGE
# ===========================
if st.session_state.current_page == "Home":
    st.header("Welcome to Smart Tree Plantation")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Why plant trees strategically?")
        st.markdown("""
        Strategic tree plantation ensures:
        - **Higher survival rates** for planted trees
        - **Better air quality** improvement
        - **Enhanced biodiversity** support
        - **Effective carbon sequestration**
        """)

        # Planting Mode Selection
        st.subheader("🏙️ Select Your Planting Space")

        planting_mode = st.radio(
            "Where are you planning to plant?",
            ["🌳 Outdoor / Yard / Ground", "🪴 Urban Balcony / Terrace / Indoor"],
            key="planting_mode_radio"
        )

        if planting_mode == "🪴 Urban Balcony / Terrace / Indoor":
            st.session_state.is_balcony_mode = True
            st.success("✅ Balcony mode activated!")

            col_space1, col_space2 = st.columns(2)
            with col_space1:
                st.session_state.space_size = st.selectbox(
                    "Available space:",
                    ["Very Small (≤ 0.5 m²)", "Small (0.5-2 m²)", "Medium (2-5 m²)", "Large (>5 m²)"],
                    index=1
                )
                st.session_state.balcony_direction = st.selectbox(
                    "Balcony direction:",
                    ["North", "East", "South", "West", "Not sure"],
                    index=1
                )

            with col_space2:
                st.session_state.sunlight_hours = st.slider(
                    "Daily sunlight (hours):",
                    0, 12, 6
                )
                st.session_state.planting_purpose = st.multiselect(
                    "Your goals:",
                    ["Air Purification", "Edible (Herbs/Vegetables)", "Aesthetic/Decor",
                     "Low Maintenance", "Medicinal", "Stress Relief"],
                    default=["Air Purification", "Low Maintenance"]
                )
        else:
            st.session_state.is_balcony_mode = False
            st.info("🌳 Outdoor mode activated!")

        # Location Input
        # --------------------------------------
        # 📍 LOCATION INPUT (GEOAPIFY VERSION)
        # --------------------------------------
        import requests

        # 🔑 Your Geoapify API key
        GEOAPIFY_API_KEY = "3d9387517a134215816c33937bf110fc"


        def geocode_address(address):
            url = "https://api.geoapify.com/v1/geocode/search"
            params = {
                "text": address,
                "apiKey": GEOAPIFY_API_KEY
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                if "features" in data and len(data["features"]) > 0:
                    feature = data["features"][0]
                    lon, lat = feature["geometry"]["coordinates"]
                    formatted_address = feature["properties"]["formatted"]
                    return formatted_address, lat, lon

            except Exception as e:
                st.error(f"Geoapify error: {e}")

            return None, None, None


        # ---- UI Starts Here ----
        st.subheader("📍 Enter your location")
        location_method = st.radio(
            "Choose location input method:",
            ["Search by address", "Use current location (requires permission)"]
        )

        # -----------------------
        # 🟥 OPTION 1: ADDRESS SEARCH
        # -----------------------
        if location_method == "Search by address":
            address = st.text_input("Enter address, city, or region:")

            if st.button("🔍 Search Location", type="primary"):
                full_addr, lat, lon = geocode_address(address)

                if lat is not None:
                    st.session_state.location = {
                        "address": full_addr,
                        "latitude": lat,
                        "longitude": lon
                    }
                    st.success(f"✅ Location found: {full_addr}")

                    # Fetch climate/soil data
                    st.session_state.climate_data = get_climate_data(lat, lon)
                    st.session_state.soil_data = get_soil_data(lat, lon)

                    # Generate recommendations
                    if st.session_state.is_balcony_mode:
                        st.session_state.recommended_trees = get_balcony_recommendations(
                            st.session_state.space_size,
                            st.session_state.sunlight_hours,
                            st.session_state.planting_purpose,
                            st.session_state.climate_data
                        )
                    else:
                        st.session_state.recommended_trees = get_recommendations(
                            st.session_state.climate_data,
                            st.session_state.soil_data
                        )

                    st.success(f"🌳 Found {len(st.session_state.recommended_trees)} recommendations!")
                    add_xp(10, "Got plant recommendations!")

                    # AUTO REDIRECT
                    st.session_state.navigate_to = "Tree Recommendations"
                    st.rerun()

                else:
                    st.error("❌ Location not found. Try another address.")


        # -----------------------
        # 🟦 OPTION 2: USE DEVICE LOCATION (unchanged)
        # -----------------------
        else:
            st.info("Click below to use your device's location")

            if st.button("📍 Get Current Location", type="primary"):
                js = """
                <script>
                function getLocation() {
                    if (!navigator.geolocation) {
                        alert('Geolocation not supported');
                        return;
                    }
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            const lat = position.coords.latitude;
                            const lon = position.coords.longitude;
                            const newUrl = window.location.pathname + '?lat=' + lat + '&lon=' + lon;
                            window.location.href = newUrl;
                        },
                        (err) => {
                            alert('Could not get location. Enable location permissions.');
                        },
                        { enableHighAccuracy: true, timeout: 10000 }
                    );
                }
                getLocation();
                </script>
                """
                components.html(js, height=0)

    with col2:
        st.subheader("Did you know?")
        st.markdown("""
        - 50%+ of mass-planted trees die within years
        - Wrong trees can deplete groundwater
        - Right urban trees reduce pollution by 60%
        """)

        st.subheader("Key Benefits")
        st.markdown("""
        - 🌱 Increased survival rate
        - 🌍 Better carbon sequestration
        - 🌤️ Improved air quality
        - 🦋 Enhanced biodiversity
        """)

# ===========================
# TREE RECOMMENDATIONS PAGE
# ===========================
elif st.session_state.current_page == "Tree Recommendations":
    st.header("🌱 Plant Recommendations")

    if st.session_state.location is None:
        st.warning("⚠️ Please set your location on the Home page first.")
        if st.button("← Go to Home", type="primary"):
            navigate_to("Home")
    else:
        # Show mode badge
        if st.session_state.is_balcony_mode:
            st.success("🪴 **Balcony Mode** - Space-efficient plants")
        else:
            st.success("🌳 **Outdoor Mode** - Ground planting trees")

        st.subheader(f"📍 {st.session_state.location['address']}")

        # Display climate and soil
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Climate Conditions")
            if st.session_state.climate_data:
                st.write(f"🌡️ Avg Temperature: {st.session_state.climate_data['avg_temp']}°C")
                st.write(f"🌧️ Annual Rainfall: {st.session_state.climate_data['annual_rainfall']} mm")
                st.write(f"💧 Humidity: {st.session_state.climate_data['humidity']}%")
                st.write(f"🌍 Climate Zone: {st.session_state.climate_data['climate_zone']}")

        with col2:
            st.subheader("Soil Conditions")
            if st.session_state.soil_data:
                st.write(f"🪨 Soil Type: {st.session_state.soil_data['soil_type']}")
                st.write(f"⚗️ pH Level: {st.session_state.soil_data['ph_level']}")
                st.write(f"💧 Drainage: {st.session_state.soil_data['drainage']}")
                st.write(f"🌱 Nutrients: {st.session_state.soil_data['nutrient_level']}")

        # Display recommendations
        st.subheader("Recommended Plants")

        if st.session_state.recommended_trees:
            # Filters
            filter_col1, filter_col2 = st.columns(2)

            with filter_col1:
                purpose_filter = st.multiselect(
                    "Filter by purpose:",
                    ["Air Purification", "Shade", "Fruit Production", "Carbon Sequestration",
                     "Biodiversity", "Edible (Herbs/Vegetables)", "Aesthetic/Decor",
                     "Low Maintenance", "Medicinal"],
                    default=[]
                )

            with filter_col2:
                growth_rate_filter = st.multiselect(
                    "Filter by growth rate:",
                    ["Fast", "Medium", "Slow"],
                    default=[]
                )

            # Apply filters
            filtered_trees = st.session_state.recommended_trees
            if purpose_filter:
                filtered_trees = [t for t in filtered_trees if any(p in t.get('purposes', []) for p in purpose_filter)]
            if growth_rate_filter:
                filtered_trees = [t for t in filtered_trees if t.get('growth_rate') in growth_rate_filter]

            # Ensure fields exist
            for item in filtered_trees:
                if 'environmental_benefits' not in item and 'benefits' in item:
                    item['environmental_benefits'] = item['benefits']
                elif 'benefits' not in item and 'environmental_benefits' in item:
                    item['benefits'] = item['environmental_benefits']

            # Display in grid
            if len(filtered_trees) == 0:
                st.warning("No plants match your filters. Adjust criteria.")
            else:
                for i in range(0, len(filtered_trees), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j < len(filtered_trees):
                            item = filtered_trees[i + j]
                            with cols[j]:
                                is_balcony = 'space_required' in item

                                if is_balcony:
                                    st.subheader(f"🪴 {item['name']}")
                                    st.write(f"**Scientific**: {item.get('scientific_name', 'N/A')}")
                                    st.write(f"**Space**: {item.get('space_required', 'N/A')}")
                                    st.write(f"**Sunlight**: {item.get('sunlight_need', 'N/A')}")
                                    st.write(f"**Watering**: {item.get('watering', 'N/A')}")
                                    st.write(f"**Difficulty**: {item.get('care_difficulty', 'N/A')}")
                                    st.write(f"**Benefits**: {item.get('benefits', 'N/A')}")
                                else:
                                    st.subheader(f"🌳 {item['name']}")
                                    st.write(f"**Scientific**: {item.get('scientific_name', 'N/A')}")
                                    st.write(f"**Growth Rate**: {item.get('growth_rate', 'N/A')}")
                                    st.write(f"**Benefits**: {item.get('environmental_benefits', 'N/A')}")

                                if st.button(f"Select {item['name']}", key=f"select_{i}_{j}"):
                                    st.session_state.selected_tree = item
                                    add_xp(5, f"Selected {item['name']}")
                                    navigate_to("Planting Guide")
        else:
            st.info("No recommendations yet. Return to Home to set location.")

# ===========================
# PLANTING GUIDE PAGE
# ===========================
elif st.session_state.current_page == "Planting Guide":
    st.header("🌱 Planting & Maintenance Guide")

    if st.session_state.selected_tree is None:
        st.warning("⚠ No plant selected. Choose one from Recommendations.")
        if st.button("← Go to Recommendations", type="primary"):
            navigate_to("Tree Recommendations")
    else:
        tree = st.session_state.selected_tree
        st.subheader(f"Guide for {tree['name']}")

        is_balcony = 'space_required' in tree

        # Plant Details
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"### {tree['name']} ({tree.get('scientific_name', 'N/A')})")

            if is_balcony:
                st.markdown(f"""
                *Space*: {tree.get('space_required', 'N/A')}  
                *Max Height*: {tree.get('max_height', 'N/A')}  
                *Sunlight*: {tree.get('sunlight_need', 'N/A')}  
                *Watering*: {tree.get('watering', 'N/A')}  
                *Difficulty*: {tree.get('care_difficulty', 'N/A')}  
                *Pot Size*: {tree.get('pot_size', 'N/A')}  
                *Benefits*: {tree.get('benefits', 'N/A')}
                """)
            else:
                st.markdown(f"""
                *Growth Rate*: {tree.get('growth_rate', 'N/A')}  
                *Mature Height*: {tree.get('mature_height', 'N/A')}  
                *Lifespan*: {tree.get('lifespan', 'N/A')}  
                *Benefits*: {tree.get('environmental_benefits', 'N/A')}
                """)

        with col2:
            st.info("🪴 Balcony Plant" if is_balcony else "🌳 Outdoor Tree")

        # Planting Steps
        st.subheader("📋 Step-by-Step Planting")

        planting_guide = get_planting_guide(tree['name'])

        if planting_guide and len(planting_guide) > 0:
            for i, step in enumerate(planting_guide, 1):
                st.markdown(f"*Step {i}*: {step}")
        else:
            # Generic guide
            if is_balcony:
                st.markdown("""
                1. Choose pot with drainage holes
                2. Fill with well-draining potting mix
                3. Plant at same depth as nursery pot
                4. Water thoroughly
                5. Place in appropriate light
                """)
            else:
                st.markdown("""
                1. Dig appropriate sized hole
                2. Plant at correct depth
                3. Water deeply
                4. Mulch around base
                5. Stake if needed
                """)

        # Maintenance Calendar
        st.subheader("📅 Seasonal Maintenance")

        maintenance = get_maintenance_guide(tree['name'])
        tabs = st.tabs(["Spring", "Summer", "Monsoon", "Winter"])

        seasons = ["Spring", "Summer", "Monsoon", "Winter"]
        for i, season in enumerate(seasons):
            with tabs[i]:
                if maintenance and season in maintenance:
                    for task in maintenance[season]:
                        st.markdown(f"- {task}")
                else:
                    st.write("Follow general care guidelines")

        # Track This Plant
        st.subheader("📊 Track This Plant")

        if st.button("✅ Add to My Garden", type="primary"):
            tree_to_track = tree.copy()
            tree_to_track['id'] = str(uuid.uuid4())  # UNIQUE ID
            tree_to_track['planted_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            tree_to_track['status'] = "Newly Planted"
            tree_to_track['health'] = "Good"

            st.session_state.planted_trees.append(tree_to_track)
            st.session_state.user_profile['trees_planted'] = len(st.session_state.planted_trees)

            add_xp(50, f"Planted {tree['name']}!")
            check_and_award_badges()

            st.success(f"✅ {tree['name']} added! View in Plant Care Tracker.")

            # AUTO-NAVIGATE
            if st.button("📊 Go to Plant Care Tracker →"):
                navigate_to("Plant Care Tracker")

# ===========================
# NEW: PLANT CARE TRACKER PAGE
# ===========================
elif st.session_state.current_page == "Plant Care Tracker":
    st.header("🌿 Plant Care Tracker")

    if not st.session_state.planted_trees:
        st.info("No plants tracked yet. Add plants from the Planting Guide!")
        if st.button("🌱 Go to Recommendations", type="primary"):
            navigate_to("Tree Recommendations")
    else:
        st.subheader("🪴 Your Garden")

        # Display all plants
        for plant in st.session_state.planted_trees:
            plant = ensure_tree_has_fields(plant)

            with st.expander(f"🌱 {plant['name']} (Planted: {plant['planted_date']})"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"*Status*: {plant['status']}")
                    st.write(f"*Health*: {plant['health']}")

                with col2:
                    # Watering log
                    plant_id = plant['id']
                    if plant_id not in st.session_state.watering_logs:
                        st.session_state.watering_logs[plant_id] = []

                    if st.button(f"💧 Log Watering", key=f"water_{plant_id}"):
                        st.session_state.watering_logs[plant_id].append(datetime.datetime.now())
                        st.success("Watered!")

                    water_count = len(st.session_state.watering_logs.get(plant_id, []))
                    st.write(f"Watered {water_count} times")

                with col3:
                    # Photo upload placeholder
                    photo = st.file_uploader(f"📸 Upload photo", key=f"photo_{plant_id}", type=['jpg', 'png'])
                    if photo:
                        st.image(photo, width=150)

                # Update health/status
                new_status = st.selectbox(
                    "Growth stage:",
                    ["Newly Planted", "Seedling", "Sapling", "Young Tree", "Mature Tree"],
                    key=f"status_{plant_id}"
                )

                new_health = st.selectbox(
                    "Health:",
                    ["Excellent", "Good", "Fair", "Needs Attention", "Poor"],
                    key=f"health_{plant_id}"
                )

                if st.button(f"Update {plant['name']}", key=f"update_{plant_id}"):
                    plant['status'] = new_status
                    plant['health'] = new_health
                    add_xp(20, "Updated plant status!")
                    st.success("Updated!")

        # Watering reminders section
        st.subheader("⏰ Upcoming Care Tasks")
        st.info("Set reminders for watering, fertilizing, pruning (Coming soon!)")


# ===========================
# IMPACT TRACKER PAGE
# ===========================
elif st.session_state.current_page == "Impact Tracker":
    st.header("📊 Environmental Impact Tracker")

    if not st.session_state.planted_trees:
        st.info("No plants tracked yet!")
        if st.button("🌱 Start Planting", type="primary"):
            navigate_to("Home")
    else:
        st.subheader("🌳 Your Tracked Plants")

        # Display as table
        df_data = []
        for plant in st.session_state.planted_trees:
            plant = ensure_tree_has_fields(plant)
            df_data.append({
                'Name': plant['name'],
                'Planted': plant['planted_date'],
                'Status': plant['status'],
                'Health': plant['health']
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

        # Environmental impact
        st.subheader("🌍 Environmental Impact")
        impact = calculate_impact(st.session_state.planted_trees)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Carbon Sequestered", f"{impact['carbon_sequestered']:.2f} kg")
        with col2:
            st.metric("Oxygen Produced", f"{impact['oxygen_produced']:.2f} kg")
        with col3:
            st.metric("Pollutants Removed", f"{impact['pollutants_removed']:.2f} g")

        # Projection chart
        st.subheader("📈 Projected Benefits (10 Years)")

        years = list(range(1, 11))
        carbon_seq = [impact['carbon_sequestered'] * (year ** 0.8) for year in years]
        oxygen_prod = [impact['oxygen_produced'] * (year ** 0.7) for year in years]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=carbon_seq, mode='lines+markers', name='Carbon (kg)'))
        fig.add_trace(go.Scatter(x=years, y=oxygen_prod, mode='lines+markers', name='Oxygen (kg)'))
        fig.update_layout(
            title='Environmental Benefits Over Time',
            xaxis_title='Years',
            yaxis_title='Amount (kg)'
        )
        st.plotly_chart(fig)

# ===========================
# COMMUNITY PAGE
# ===========================
elif st.session_state.current_page == "Community":
    display_community_feed()

# ===========================
# ABOUT PAGE
# ===========================

# About page
# ----------------------
# About page
# ----------------------
elif st.session_state.current_page == "About":
    st.header("About the Tree Plantation Planner")

    st.subheader("Project Objective")
    st.markdown("""
    The Tree Plantation Planner is designed to guide people in making smarter planting choices. 
    By recommending the right trees for the right places, it ensures that tree plantation efforts actually 
    benefit the environment, improve air quality, and support biodiversity.
    """)

    st.subheader("Why We Created This Tool")
    st.markdown("""
    Across the world, large-scale afforestation efforts are undertaken to fight climate change, 
    improve air quality, and restore ecosystems. However, many of these efforts fail to produce 
    real impact because:

    - Trees are planted randomly without considering local soil, climate, and biodiversity  
    - High mortality rates leave behind empty land instead of thriving forests  
    - Inappropriate tree choices damage ecosystems rather than restoring them  

    This project aims to fix these problems by helping individuals, communities, and policymakers 
    choose the right trees for the right places.
    """)

    st.subheader("Balcony Plantation")
    st.markdown("""
    Not everyone has access to large open spaces—but **everyone can still contribute** to the planet.

    ### 🌱 Why Balcony Plantation Matters
    Balcony plants:
    - Improve indoor and outdoor air quality  
    - Increase oxygen levels in compact urban homes  
    - Reduce heat in apartments through natural cooling  
    - Support pollinators like butterflies and bees  
    - Boost mental well-being and reduce stress  

    Even a single balcony garden can make a measurable environmental difference in densely populated cities.

    ### 🌿 How The Planner Helps Balcony Gardeners
    Our system provides:
    - **Personalized balcony plant recommendations** based on sunlight exposure, pot size, and climate  
    - **Low-maintenance plant options** for beginners  
    - **Native balcony plant suggestions** that survive longer and support biodiversity  
    - **Growth and care guidelines** tailored to small spaces  
    - **Impact tracking** so users can measure the environmental benefit of their balcony garden  

    This helps people living in cities create a greener lifestyle using the limited space they have— 
    turning balconies into mini-ecosystems with meaningful environmental impact.
    """)

    st.subheader("Social Impact")
    st.markdown("""
    Planting trees isn't just about filling up empty spaces—it's about making a difference. This project will:

    - Reduce air pollution by increasing tree cover in high-pollution areas  
    - Improve public health by filtering pollutants and providing cleaner air  
    - Enhance biodiversity by promoting native trees that sustain ecosystems  
    - Encourage community participation, making tree plantation a shared responsibility  

    With this approach, tree plantation becomes more than just a symbolic act—it becomes a powerful environmental tool.
    """)

    st.subheader("Research & Data Sources")
    st.markdown("""
    This project is backed by scientific research and real-world data:

    - World Health Organization (WHO) – Reports on urban forestry and air pollution  
    - NASA Climate Change Data – Research on deforestation and afforestation impact  
    - IPCC Climate Reports (2023) – Studies on afforestation as a climate change solution  
    - Food and Agriculture Organization (FAO) Report (2023) – Global forest mortality studies  
    """)

# Footer
st.markdown("---")
st.markdown("Tree Plantation Planner | A data-driven approach to smarter afforestation")
