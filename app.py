# app.py (cleaned version)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import requests
import datetime

# Import custom modules (assumed to exist)
from tree_data import get_tree_data, get_tree_details
from recommendation import get_recommendations
from climate_data import get_climate_data
from soil_data import get_soil_types, get_soil_data
from impact_calculator import calculate_impact
from utils import display_tree_svg
from planting_guide import get_planting_guide, get_maintenance_guide

# -----------------------------
# Geoapify geocoding helper
# -----------------------------
GEOAPIFY_API_KEY = "3d9387517a134215816c33937bf110fc"

def geocode_address(address_or_latlon):
    """
    If address_or_latlon is a pair "lat, lon" or two floats separated by comma,
    perform reverse geocode. Otherwise do forward geocode.
    Returns: (formatted_address_or_None, lat_or_None, lon_or_None)
    """
    try:
        # Reverse geocode if looks like "lat, lon"
        if isinstance(address_or_latlon, str) and "," in address_or_latlon:
            parts = [p.strip() for p in address_or_latlon.split(",")]
            if len(parts) >= 2:
                try:
                    lat = float(parts[0])
                    lon = float(parts[1])
                    url = "https://api.geoapify.com/v1/geocode/reverse"
                    params = {"lat": lat, "lon": lon, "apiKey": GEOAPIFY_API_KEY}
                    r = requests.get(url, params=params, timeout=10)
                    r.raise_for_status()
                    data = r.json()
                    if data.get("features"):
                        feat = data["features"][0]
                        formatted = feat["properties"].get("formatted", f"{lat}, {lon}")
                        return formatted, lat, lon
                    return None, lat, lon
                except ValueError:
                    # Not numeric -> fall back to forward geocode
                    pass

        # Forward geocode
        url = "https://api.geoapify.com/v1/geocode/search"
        params = {"text": address_or_latlon, "apiKey": GEOAPIFY_API_KEY, "limit": 1}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "features" in data and len(data["features"]) > 0:
            feat = data["features"][0]
            lon, lat = feat["geometry"]["coordinates"]
            formatted = feat["properties"].get("formatted", None)
            return formatted, lat, lon

    except Exception as exc:
        # Surface an error to Streamlit UI but don't raise so app keeps running
        try:
            st.error(f"Geocoding (Geoapify) error: {exc}")
        except Exception:
            pass

    return None, None, None

# -----------------------------

# Page config
st.set_page_config(
    page_title="Tree Plantation Planner",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state keys if missing
if 'location' not in st.session_state:
    st.session_state.location = None
if 'climate_data' not in st.session_state:
    st.session_state.climate_data = None
if 'soil_data' not in st.session_state:
    st.session_state.soil_data = None
if 'recommended_trees' not in st.session_state:
    st.session_state.recommended_trees = None
if 'selected_tree' not in st.session_state:
    st.session_state.selected_tree = None
if 'planted_trees' not in st.session_state:
    st.session_state.planted_trees = []

# App header
st.title("🌳 Tree Plantation Planner")
st.markdown("""
A data-driven approach to planting the right trees in the right places.
This tool helps you make informed decisions about tree plantation based on location, climate, and soil conditions.
""")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Tree Recommendations", "Planting Guide", "Impact Tracker", "About the Project"]
)

# Sidebar artwork / small svg
display_tree_svg()

# --------------------------
# HOME PAGE
# --------------------------
if page == "Home":
    st.header("Welcome to Smart Tree Plantation")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Why plant trees strategically?")
        st.markdown("""
        Random tree planting without considering local climate, soil, and biodiversity can do more harm than good.
        Strategic tree plantation ensures:
        - **Higher survival rates** for planted trees
        - **Better air quality** improvement
        - **Enhanced biodiversity** support
        - **Effective carbon sequestration**
        - **Sustainable ecological balance**
        Start by selecting your location to get tree recommendations tailored to your area.
        """)

        # LOCATION input UI
        st.subheader("Enter your location")
        location_method = st.radio("Choose location input method:",
                                   ["Search by address", "Use current location (requires permission)"])

        if location_method == "Search by address":
            address = st.text_input("Enter address, city, or region:")
            if st.button("Search Location"):
                try:
                    full_addr, lat, lon = geocode_address(address)

                    # Ensure we have coordinates
                    if lat is not None and lon is not None:
                        st.session_state.location = {
                            "address": full_addr if full_addr else address,
                            "latitude": lat,
                            "longitude": lon
                        }
                        st.success(f"Location found: {st.session_state.location['address']}")

                        # Get climate and soil data
                        st.session_state.climate_data = get_climate_data(lat, lon)
                        st.session_state.soil_data = get_soil_data(lat, lon)

                        # Generate recommendations
                        st.session_state.recommended_trees = get_recommendations(
                            st.session_state.climate_data,
                            st.session_state.soil_data
                        )

                        st.info("Go to 'Tree Recommendations' to see suitable trees for your location")
                    else:
                        st.error("Location not found. Please try a different address.")
                except Exception as e:
                    st.error(f"Error locating address: {str(e)}")
        else:
            st.info("Please allow location access when prompted by your browser.")
            if st.button("Get Current Location"):
                # fallback / placeholder for device location — you can replace with JS method if desired
                st.session_state.location = {
                    "address": "New Delhi, India",
                    "latitude": 28.6139,
                    "longitude": 77.2090
                }
                st.success(f"Using location: {st.session_state.location['address']}")

                # Get climate and soil data
                lat = st.session_state.location['latitude']
                lon = st.session_state.location['longitude']
                st.session_state.climate_data = get_climate_data(lat, lon)
                st.session_state.soil_data = get_soil_data(lat, lon)

                # Generate recommendations
                st.session_state.recommended_trees = get_recommendations(
                    st.session_state.climate_data,
                    st.session_state.soil_data
                )
                st.info("Go to 'Tree Recommendations' to see suitable trees for your location")

    with col2:
        st.subheader("Did you know?")
        st.markdown("""
        - Over 50% of trees planted in mass afforestation projects die within a few years
        - Planting the wrong trees can deplete groundwater reserves
        - Urban green spaces with the right trees can reduce air pollution by up to 60%
        - Grasslands and wetlands sometimes store more carbon than forests
        """)
        st.subheader("Key Benefits")
        st.markdown("""
        - 🌱 Increased tree survival rate 
        - 🌍 Better carbon sequestration
        - 🌤️ Improved air quality
        - 🐝 Enhanced biodiversity
        - 💧 Water conservation
        """)

# --------------------------
# TREE RECOMMENDATIONS
# --------------------------
elif page == "Tree Recommendations":
    st.header("Tree Recommendations")

    if st.session_state.location is None:
        st.warning("Please enter your location on the Home page first.")
    else:
        st.subheader(f"Location: {st.session_state.location['address'] if st.session_state.location else 'Unknown'}")

        # Display climate and soil data
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Climate Conditions")
            if st.session_state.climate_data:
                # Defensive get to avoid KeyError
                cd = st.session_state.climate_data
                st.write(f"Average Temperature: {cd.get('avg_temp', 'N/A')}°C")
                st.write(f"Annual Rainfall: {cd.get('annual_rainfall', 'N/A')} mm")
                st.write(f"Humidity: {cd.get('humidity', 'N/A')}%")
                st.write(f"Climate Zone: {cd.get('climate_zone', 'N/A')}")
            else:
                st.info("Climate data not available")

        with col2:
            st.subheader("Soil Conditions")
            if st.session_state.soil_data:
                sd = st.session_state.soil_data
                st.write(f"Soil Type: {sd.get('soil_type', 'N/A')}")
                st.write(f"pH Level: {sd.get('ph_level', 'N/A')}")
                st.write(f"Drainage: {sd.get('drainage', 'N/A')}")
                st.write(f"Nutrient Level: {sd.get('nutrient_level', 'N/A')}")
            else:
                st.info("Soil data not available")

        # Display recommended trees
        st.subheader("Recommended Trees for Your Location")
        if st.session_state.recommended_trees:
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                purpose_filter = st.multiselect(
                    "Filter by purpose:",
                    ["Air Purification", "Shade", "Fruit Production", "Carbon Sequestration", "Biodiversity"],
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
                filtered_trees = [tree for tree in filtered_trees
                                  if any(p in tree.get('purposes', []) for p in purpose_filter)]
            if growth_rate_filter:
                filtered_trees = [tree for tree in filtered_trees
                                  if tree.get('growth_rate') in growth_rate_filter]

            # Display trees in rows of 3
            num_trees = len(filtered_trees)
            if num_trees == 0:
                st.warning("No trees match your filter criteria. Please adjust your filters.")
            else:
                for i in range(0, num_trees, 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j < num_trees:
                            tree = filtered_trees[i + j]
                            with cols[j]:
                                st.subheader(tree.get('name', 'Unknown'))
                                st.write(f"**Scientific Name**: {tree.get('scientific_name', 'N/A')}")
                                st.write(f"**Growth Rate**: {tree.get('growth_rate', 'N/A')}")
                                st.write(f"**Purposes**: {', '.join(tree.get('purposes', []))}")
                                st.write(f"**Environmental Benefits**: {tree.get('environmental_benefits', 'N/A')}")

                                if st.button(f"Select {tree.get('name', 'tree')}", key=f"tree_{i+j}"):
                                    st.session_state.selected_tree = tree
                                    st.info(f"You've selected {tree.get('name', 'this tree')}. Go to 'Planting Guide' for detailed instructions.")
        else:
            st.info("No tree recommendations available. Please return to the Home page and enter your location.")

# --------------------------
# PLANTING GUIDE
# --------------------------
elif page == "Planting Guide":
    st.header("Tree Planting & Maintenance Guide")

    if st.session_state.selected_tree is None:
        st.warning("Please select a tree from the Recommendations page first.")
    else:
        tree = st.session_state.selected_tree
        st.subheader(f"Planting Guide for {tree.get('name', 'Unknown')}")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""
            ### {tree.get('name', 'Unknown')} ({tree.get('scientific_name', '')})
            **Growth Rate**: {tree.get('growth_rate', 'N/A')}  
            **Mature Height**: {tree.get('mature_height', 'N/A')}  
            **Lifespan**: {tree.get('lifespan', 'N/A')}  
            **Native Region**: {tree.get('native_region', 'N/A')}  

            **Environmental Benefits**:  
            {tree.get('environmental_benefits', 'N/A')}

            **Best suited for**: {', '.join(tree.get('purposes', []))}
            """)

        st.subheader("Step-by-Step Planting Guide")
        planting_guide = get_planting_guide(tree.get('name', ''))
        if planting_guide:
            for i, step in enumerate(planting_guide, 1):
                st.markdown(f"**Step {i}**: {step}")
        else:
            st.write("No specific planting guide available.")

        st.subheader("Maintenance Calendar")
        maintenance = get_maintenance_guide(tree.get('name', ''))
        tabs = st.tabs(["Spring", "Summer", "Monsoon", "Winter"])
        seasons = ["Spring", "Summer", "Monsoon", "Winter"]
        for i, season in enumerate(seasons):
            with tabs[i]:
                if maintenance and season in maintenance:
                    for task in maintenance[season]:
                        st.markdown(f"- {task}")
                else:
                    st.write("No specific tasks for this season.")

        if st.button("Track This Tree"):
            tree_to_track = tree.copy()
            tree_to_track['planted_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            tree_to_track['status'] = "Newly Planted"
            tree_to_track['health'] = "Good"
            st.session_state.planted_trees.append(tree_to_track)
            st.success(f"{tree.get('name', 'Tree')} added to your tracked trees. View in 'Impact Tracker'.")

# --------------------------
# IMPACT TRACKER
# --------------------------
elif page == "Impact Tracker":
    st.header("Tree Impact Tracker")

    if not st.session_state.planted_trees:
        st.info("You haven't tracked any trees yet. Go to 'Planting Guide' to track trees.")
    else:
        st.subheader("Your Tracked Trees")
        tracked_trees_df = pd.DataFrame(st.session_state.planted_trees)
        cols_to_show = [c for c in ['name', 'planted_date', 'status', 'health'] if c in tracked_trees_df.columns]
        if not tracked_trees_df.empty:
            st.dataframe(tracked_trees_df[cols_to_show])
        else:
            st.write("No tracked trees available.")

        st.subheader("Update Tree Status")
        tree_names = [tree.get('name', 'Unknown') for tree in st.session_state.planted_trees]
        tree_to_update = st.selectbox("Select tree to update:", tree_names)

        col1, col2 = st.columns(2)
        with col1:
            new_status = st.selectbox(
                "Current growth stage:",
                ["Newly Planted", "Seedling", "Sapling", "Young Tree", "Mature Tree"]
            )
        with col2:
            new_health = st.selectbox(
                "Current health:",
                ["Excellent", "Good", "Fair", "Needs Attention", "Poor"]
            )

        if st.button("Update Status"):
            for tree in st.session_state.planted_trees:
                if tree.get('name') == tree_to_update:
                    tree['status'] = new_status
                    tree['health'] = new_health
                    break
            st.success(f"Status updated for {tree_to_update}")

        # Calculate environmental impact
        st.subheader("Environmental Impact")
        impact = calculate_impact(st.session_state.planted_trees)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Carbon Sequestered", f"{impact.get('carbon_sequestered', 0):.2f} kg")
        with col2:
            st.metric("Oxygen Produced", f"{impact.get('oxygen_produced', 0):.2f} kg")
        with col3:
            st.metric("Air Pollutants Removed", f"{impact.get('pollutants_removed', 0):.2f} g")

        # Visualize impact over time
        st.subheader("Impact Over Time")
        years = list(range(1, 11))
        carbon_seq = [impact.get('carbon_sequestered', 0) * (year ** 0.8) for year in years]
        oxygen_prod = [impact.get('oxygen_produced', 0) * (year ** 0.7) for year in years]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=carbon_seq, mode='lines+markers', name='Carbon Sequestered (kg)'))
        fig.add_trace(go.Scatter(x=years, y=oxygen_prod, mode='lines+markers', name='Oxygen Produced (kg)'))
        fig.update_layout(title='Projected Environmental Benefits Over 10 Years',
                          xaxis_title='Years', yaxis_title='Amount (kg)', legend_title='Benefit Type')
        st.plotly_chart(fig)

# --------------------------
# ABOUT PAGE
# --------------------------
elif page == "About the Project":
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
    """)
    st.subheader("Social Impact")
    st.markdown("""
    Planting trees isn't just about filling up empty spaces—it's about making a difference. This project will:
    - Reduce air pollution by increasing tree cover in high-pollution areas
    - Improve public health by filtering pollutants and providing cleaner air
    - Enhance biodiversity by promoting native trees that sustain ecosystems
    - Encourage community participation, making tree plantation a shared responsibility
    """)
    st.subheader("Research & Data Sources")
    st.markdown("""
    This project is backed by scientific research and real-world data:
    - World Health Organization (WHO)
    - NASA Climate Change Data
    - IPCC Climate Reports
    - Food and Agriculture Organization (FAO) Reports
    """)

# Footer
st.markdown("---")
st.markdown("Tree Plantation Planner | A data-driven approach to smarter afforestation")
