import streamlit as st
import pandas as pd
import geopy
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Import custom modules
from tree_data import get_tree_data, get_tree_details
from recommendation import get_recommendations
from climate_data import get_climate_data
from soil_data import get_soil_types, get_soil_data
from impact_calculator import calculate_impact
from utils import display_tree_svg
from planting_guide import get_planting_guide, get_maintenance_guide

# Set page configuration
st.set_page_config(
    page_title="Tree Plantation Planner",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
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

# App title and header
st.title("🌳 Tree Plantation Planner")
st.markdown("""
A data-driven approach to planting the right trees in the right places. 
This tool helps you make informed decisions about tree plantation based on location, climate, and soil conditions.
""")

# Sidebar for navigation
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Tree Recommendations", "Planting Guide", "Impact Tracker", "About the Project"]
)

# Display tree SVG in sidebar
display_tree_svg()

# Home page
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
        
        # Location input
        st.subheader("Enter your location")
        location_method = st.radio("Choose location input method:", 
                                   ["Search by address", "Use current location (requires permission)"])
        
        if location_method == "Search by address":
            address = st.text_input("Enter address, city, or region:")
            if st.button("Search Location"):
                try:
                    geolocator = Nominatim(user_agent="tree_planner")
                    location = geolocator.geocode(address)
                    if location:
                        st.session_state.location = {
                            "address": location.address,
                            "latitude": location.latitude,
                            "longitude": location.longitude
                        }
                        st.success(f"Location found: {location.address}")
                        
                        # Get climate and soil data
                        st.session_state.climate_data = get_climate_data(
                            location.latitude, 
                            location.longitude
                        )
                        st.session_state.soil_data = get_soil_data(
                            location.latitude, 
                            location.longitude
                        )
                        
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
                # In a real implementation, we would use JavaScript to get the exact location
                # For this sample, we'll use a default location (New Delhi, India)
                st.session_state.location = {
                    "address": "New Delhi, India",
                    "latitude": 28.6139,
                    "longitude": 77.2090
                }
                
                st.success(f"Using location: {st.session_state.location['address']}")
                
                # Get climate and soil data
                st.session_state.climate_data = get_climate_data(
                    st.session_state.location['latitude'], 
                    st.session_state.location['longitude']
                )
                st.session_state.soil_data = get_soil_data(
                    st.session_state.location['latitude'], 
                    st.session_state.location['longitude']
                )
                
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

# Tree Recommendations page
elif page == "Tree Recommendations":
    st.header("Tree Recommendations")
    
    if st.session_state.location is None:
        st.warning("Please enter your location on the Home page first.")
    else:
        st.subheader(f"Location: {st.session_state.location['address']}")
        
        # Display climate and soil data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Climate Conditions")
            if st.session_state.climate_data:
                st.write(f"Average Temperature: {st.session_state.climate_data['avg_temp']}°C")
                st.write(f"Annual Rainfall: {st.session_state.climate_data['annual_rainfall']} mm")
                st.write(f"Humidity: {st.session_state.climate_data['humidity']}%")
                st.write(f"Climate Zone: {st.session_state.climate_data['climate_zone']}")
            else:
                st.info("Climate data not available")
        
        with col2:
            st.subheader("Soil Conditions")
            if st.session_state.soil_data:
                st.write(f"Soil Type: {st.session_state.soil_data['soil_type']}")
                st.write(f"pH Level: {st.session_state.soil_data['ph_level']}")
                st.write(f"Drainage: {st.session_state.soil_data['drainage']}")
                st.write(f"Nutrient Level: {st.session_state.soil_data['nutrient_level']}")
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
                                if any(purpose in tree['purposes'] for purpose in purpose_filter)]
            if growth_rate_filter:
                filtered_trees = [tree for tree in filtered_trees 
                                if tree['growth_rate'] in growth_rate_filter]
            
            # Display trees in a grid
            num_trees = len(filtered_trees)
            if num_trees == 0:
                st.warning("No trees match your filter criteria. Please adjust your filters.")
            else:
                # Display trees in rows of 3
                for i in range(0, num_trees, 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j < num_trees:
                            tree = filtered_trees[i + j]
                            with cols[j]:
                                st.subheader(tree['name'])
                                st.write(f"**Scientific Name**: {tree['scientific_name']}")
                                st.write(f"**Growth Rate**: {tree['growth_rate']}")
                                st.write(f"**Purposes**: {', '.join(tree['purposes'])}")
                                st.write(f"**Environmental Benefits**: {tree['environmental_benefits']}")
                                
                                if st.button(f"Select {tree['name']}", key=f"tree_{i+j}"):
                                    st.session_state.selected_tree = tree
                                    st.info(f"You've selected {tree['name']}. Go to 'Planting Guide' for detailed instructions.")
        else:
            st.info("No tree recommendations available. Please return to the Home page and enter your location.")

# Planting Guide page
elif page == "Planting Guide":
    st.header("Tree Planting & Maintenance Guide")
    
    if st.session_state.selected_tree is None:
        st.warning("Please select a tree from the Recommendations page first.")
    else:
        tree = st.session_state.selected_tree
        st.subheader(f"Planting Guide for {tree['name']}")
        
        # Tree details
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""
            ### {tree['name']} ({tree['scientific_name']})
            
            **Growth Rate**: {tree['growth_rate']}  
            **Mature Height**: {tree['mature_height']}  
            **Lifespan**: {tree['lifespan']}  
            **Native Region**: {tree['native_region']}  
            
            **Environmental Benefits**:  
            {tree['environmental_benefits']}
            
            **Best suited for**: {', '.join(tree['purposes'])}
            """)
        
        # Planting steps
        st.subheader("Step-by-Step Planting Guide")
        planting_guide = get_planting_guide(tree['name'])
        
        for i, step in enumerate(planting_guide, 1):
            st.markdown(f"**Step {i}**: {step}")
        
        # Maintenance calendar
        st.subheader("Maintenance Calendar")
        maintenance = get_maintenance_guide(tree['name'])
        
        # Create tabs for seasons
        tabs = st.tabs(["Spring", "Summer", "Monsoon", "Winter"])
        
        for i, season in enumerate(["Spring", "Summer", "Monsoon", "Winter"]):
            with tabs[i]:
                if season in maintenance:
                    for task in maintenance[season]:
                        st.markdown(f"- {task}")
                else:
                    st.write("No specific maintenance tasks for this season.")
        
        # Add to planted trees
        if st.button("Track This Tree"):
            # Add current date and initial status
            import datetime
            tree_to_track = tree.copy()
            tree_to_track['planted_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            tree_to_track['status'] = "Newly Planted"
            tree_to_track['health'] = "Good"
            
            st.session_state.planted_trees.append(tree_to_track)
            st.success(f"{tree['name']} added to your tracked trees. View in 'Impact Tracker'.")

# Impact Tracker page
elif page == "Impact Tracker":
    st.header("Tree Impact Tracker")
    
    if not st.session_state.planted_trees:
        st.info("You haven't tracked any trees yet. Go to 'Planting Guide' to track trees.")
    else:
        st.subheader("Your Tracked Trees")
        
        # Table of tracked trees
        tracked_trees_df = pd.DataFrame(st.session_state.planted_trees)
        st.dataframe(tracked_trees_df[['name', 'planted_date', 'status', 'health']])
        
        # Update tree status
        st.subheader("Update Tree Status")
        tree_names = [tree['name'] for tree in st.session_state.planted_trees]
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
                if tree['name'] == tree_to_update:
                    tree['status'] = new_status
                    tree['health'] = new_health
                    break
            st.success(f"Status updated for {tree_to_update}")
        
        # Calculate environmental impact
        st.subheader("Environmental Impact")
        impact = calculate_impact(st.session_state.planted_trees)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Carbon Sequestered", f"{impact['carbon_sequestered']:.2f} kg")
        with col2:
            st.metric("Oxygen Produced", f"{impact['oxygen_produced']:.2f} kg")
        with col3:
            st.metric("Air Pollutants Removed", f"{impact['pollutants_removed']:.2f} g")
        
        # Visualize impact over time
        st.subheader("Impact Over Time")
        st.write("As your trees grow, their environmental benefits increase:")
        
        # Generate time series data for visualization
        years = list(range(1, 11))
        carbon_seq = [impact['carbon_sequestered'] * (year ** 0.8) for year in years]
        oxygen_prod = [impact['oxygen_produced'] * (year ** 0.7) for year in years]
        
        # Create line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=carbon_seq, mode='lines+markers', name='Carbon Sequestered (kg)'))
        fig.add_trace(go.Scatter(x=years, y=oxygen_prod, mode='lines+markers', name='Oxygen Produced (kg)'))
        fig.update_layout(
            title='Projected Environmental Benefits Over 10 Years',
            xaxis_title='Years',
            yaxis_title='Amount (kg)',
            legend_title='Benefit Type'
        )
        st.plotly_chart(fig)

# About page
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
    
    This project aims to fix these problems by helping individuals, communities, and policymakers 
    choose the right trees for the right places.
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
st.markdown(
    "© 2023 Tree Plantation Planner | A data-driven approach to smarter afforestation"
)
