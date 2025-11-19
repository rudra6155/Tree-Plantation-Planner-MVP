import streamlit as st
import pandas as pd
from community import initialize_community, display_community_feed
import geopy
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Import custom modules
from tree_data import get_tree_data, get_tree_details
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
# NEW: Add these lines
if 'is_balcony_mode' not in st.session_state:
    st.session_state.is_balcony_mode = False
if 'space_size' not in st.session_state:
    st.session_state.space_size = 'Small (0.5-2 m²)'
if 'sunlight_hours' not in st.session_state:
    st.session_state.sunlight_hours = 6
if 'planting_purpose' not in st.session_state:
    st.session_state.planting_purpose = []
if 'balcony_direction' not in st.session_state:
    st.session_state.balcony_direction = 'East'
    # Initialize user profile and update streak
    initialize_user_profile()
    # Initialize community
    initialize_community()
    update_streak()
# App title and header
st.title("🌳 Tree Plantation Planner")
st.markdown("""
A data-driven approach to planting the right trees in the right places. 
This tool helps you make informed decisions about tree plantation based on location, climate, and soil conditions.
""")

# Sidebar for navigation
# Display user profile in sidebar
display_profile_sidebar()

# Sidebar for navigation
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Tree Recommendations", "Planting Guide", "Impact Tracker", "Community", "About"]
)

# Display tree SVG
display_tree_svg()

# Display tree SVG in sidebar
display_tree_svg()

# Home page
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

        # ---------- NEW: Urban / Balcony Mode Selection ----------
        st.subheader("🏙️ Select Your Planting Space")

        planting_mode = st.radio(
            "Where are you planning to plant?",
            ["🌳 Outdoor / Yard / Ground", "🪴 Urban Balcony / Terrace / Indoor"],
            key="planting_mode_radio"
        )

        # CRITICAL: Set session state IMMEDIATELY when radio changes
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
                    "Balcony/Terrace direction:",
                    ["North", "East", "South", "West", "Not sure"],
                    index=1
                )

            with col_space2:
                st.session_state.sunlight_hours = st.slider(
                    "Average daily sunlight (hours):",
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

        # DEBUG INFO (Remove this later)
        with st.expander("🔍 Debug Info - Current Settings"):
            st.write("**Is Balcony Mode:**", st.session_state.is_balcony_mode)
            st.write("**Space Size:**", st.session_state.get('space_size', 'Not set'))
            st.write("**Sunlight Hours:**", st.session_state.get('sunlight_hours', 'Not set'))
            st.write("**Purpose:**", st.session_state.get('planting_purpose', 'Not set'))
        # ---------- END NEW SECTION ----------

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

                        # Generate recommendations based on mode
                        if st.session_state.is_balcony_mode:
                            st.info("🪴 Generating balcony plant recommendations...")
                            st.session_state.recommended_trees = get_balcony_recommendations(
                                st.session_state.space_size,
                                st.session_state.sunlight_hours,
                                st.session_state.planting_purpose,
                                st.session_state.climate_data
                            )
                            st.success(f"✅ Found {len(st.session_state.recommended_trees)} balcony-friendly plants!")
                        else:
                            st.info("🌳 Generating outdoor tree recommendations...")
                            st.session_state.recommended_trees = get_recommendations(
                                st.session_state.climate_data,
                                st.session_state.soil_data
                            )
                            st.success(f"✅ Found {len(st.session_state.recommended_trees)} trees!")

                        st.info("Go to 'Tree Recommendations' to see suitable trees for your location")
                        # After: st.session_state.recommended_trees = get_...
                        add_xp(10, "Got plant recommendations!")
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

                # Generate recommendations based on mode
                if st.session_state.is_balcony_mode:
                    st.info("🪴 Generating balcony plant recommendations...")
                    st.session_state.recommended_trees = get_balcony_recommendations(
                        st.session_state.space_size,
                        st.session_state.sunlight_hours,
                        st.session_state.planting_purpose,
                        st.session_state.climate_data
                    )
                    st.success(f"✅ Found {len(st.session_state.recommended_trees)} balcony-friendly plants!")
                else:
                    st.info("🌳 Generating outdoor tree recommendations...")
                    st.session_state.recommended_trees = get_recommendations(
                        st.session_state.climate_data,
                        st.session_state.soil_data
                    )
                    st.success(f"✅ Found {len(st.session_state.recommended_trees)} trees!")

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
        - 🦋 Enhanced biodiversity
        - 💧 Water conservation
        """)
# Tree Recommendations page
# Tree Recommendations page
elif page == "Tree Recommendations":
    st.header("🌱 Plant Recommendations")

    if st.session_state.location is None:
        st.warning("Please enter your location on the Home page first.")
    else:
        # Show mode badge
        if st.session_state.get('is_balcony_mode', False):
            st.success("🪴 **Balcony/Urban Mode** - Showing space-efficient plants")
        else:
            st.success("🌳 **Outdoor Mode** - Showing trees for ground planting")

        st.subheader(f"📍 Location: {st.session_state.location['address']}")

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

        # Display recommended trees/plants
        st.subheader("Recommended Plants for Your Space")
        if st.session_state.recommended_trees:
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
                filtered_trees = [tree for tree in filtered_trees
                                  if any(purpose in tree.get('purposes', []) for purpose in purpose_filter)]
            if growth_rate_filter:
                filtered_trees = [tree for tree in filtered_trees
                                  if tree.get('growth_rate') in growth_rate_filter]

            # Ensure backward compatibility - add missing fields
            for item in filtered_trees:
                if 'environmental_benefits' not in item and 'benefits' in item:
                    item['environmental_benefits'] = item['benefits']
                elif 'benefits' not in item and 'environmental_benefits' in item:
                    item['benefits'] = item['environmental_benefits']

            # Display trees in a grid
            num_items = len(filtered_trees)
            if num_items == 0:
                st.warning("No plants match your filter criteria. Please adjust your filters.")
            else:
                # Display in rows of 3
                for i in range(0, num_items, 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j < num_items:
                            item = filtered_trees[i + j]
                            with cols[j]:
                                # Check if it's balcony mode or outdoor mode
                                is_balcony_plant = 'space_required' in item

                                if is_balcony_plant:
                                    # BALCONY PLANT DISPLAY
                                    st.subheader(f"🪴 {item['name']}")
                                    st.write(f"**Scientific Name**: {item.get('scientific_name', 'N/A')}")
                                    st.write(f"**Space Needed**: {item.get('space_required', 'N/A')}")
                                    st.write(f"**Sunlight**: {item.get('sunlight_need', 'N/A')}")
                                    st.write(f"**Watering**: {item.get('watering', 'N/A')}")
                                    st.write(f"**Care Difficulty**: {item.get('care_difficulty', 'N/A')}")
                                    st.write(f"**Pot Size**: {item.get('pot_size', 'N/A')}")
                                    st.write(f"**Purposes**: {', '.join(item.get('purposes', []))}")
                                    st.write(
                                        f"**Benefits**: {item.get('benefits', item.get('environmental_benefits', 'N/A'))}")
                                    st.write(f"**Ideal For**: {item.get('ideal_for', 'N/A')}")
                                else:
                                    # OUTDOOR TREE DISPLAY
                                    st.subheader(f"🌳 {item['name']}")
                                    st.write(f"**Scientific Name**: {item.get('scientific_name', 'N/A')}")
                                    st.write(f"**Growth Rate**: {item.get('growth_rate', 'N/A')}")
                                    st.write(f"**Purposes**: {', '.join(item.get('purposes', []))}")
                                    st.write(
                                        f"**Environmental Benefits**: {item.get('environmental_benefits', item.get('benefits', 'N/A'))}")

                                # Inside the button click:
                                if st.button(f"Select {item['name']}", key=f"item_{i + j}"):
                                    st.session_state.selected_tree = item
                                    add_xp(5, f"Selected {item['name']}")
                                    st.info(f"✅ Selected {item['name']}. Go to 'Planting Guide' for details.")
        else:
            st.info("No tree recommendations available. Please return to the Home page and enter your location.")
# Planting Guide page
# Planting Guide page
elif page == "Planting Guide":
    st.header("Tree Planting & Maintenance Guide")

    if st.session_state.selected_tree is None:
        st.warning("Please select a tree from the Recommendations page first.")
    else:
        tree = st.session_state.selected_tree
        st.subheader(f"Planting Guide for {tree['name']}")

        # Check if it's a balcony plant or outdoor tree
        is_balcony = 'space_required' in tree

        # Tree details
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"### {tree['name']} ({tree.get('scientific_name', 'N/A')})")

            if is_balcony:
                # BALCONY PLANT DETAILS
                st.markdown(f"""
                **Space Required**: {tree.get('space_required', 'N/A')}  
                **Max Height**: {tree.get('max_height', 'N/A')}  
                **Growth Rate**: {tree.get('growth_rate', 'N/A')}  
                **Care Difficulty**: {tree.get('care_difficulty', 'N/A')}  
                **Sunlight Need**: {tree.get('sunlight_need', 'N/A')}  
                **Watering**: {tree.get('watering', 'N/A')}  
                **Pot Size**: {tree.get('pot_size', 'N/A')}  

                **Benefits**:  
                {tree.get('benefits', tree.get('environmental_benefits', 'N/A'))}

                **Best suited for**: {tree.get('ideal_for', ', '.join(tree.get('purposes', [])))}
                """)
            else:
                # OUTDOOR TREE DETAILS
                st.markdown(f"""
                **Growth Rate**: {tree.get('growth_rate', 'N/A')}  
                **Mature Height**: {tree.get('mature_height', 'N/A')}  
                **Lifespan**: {tree.get('lifespan', 'N/A')}  
                **Native Region**: {tree.get('native_region', 'N/A')}  

                **Environmental Benefits**:  
                {tree.get('environmental_benefits', tree.get('benefits', 'N/A'))}

                **Best suited for**: {', '.join(tree.get('purposes', []))}
                """)

        with col2:
            # Display icon or image placeholder
            if is_balcony:
                st.info("🪴 Balcony Plant")
            else:
                st.info("🌳 Outdoor Tree")

        # Planting steps
        st.subheader("Step-by-Step Planting Guide")

        # Get planting guide - use tree name
        try:
            planting_guide = get_planting_guide(tree['name'])

            if planting_guide and len(planting_guide) > 0:
                for i, step in enumerate(planting_guide, 1):
                    st.markdown(f"**Step {i}**: {step}")
            else:
                # Generic planting guide if specific one not available
                if is_balcony:
                    st.markdown("""
                    **Step 1**: Choose a pot with drainage holes (size: {})

                    **Step 2**: Fill pot with well-draining potting mix

                    **Step 3**: Plant at the same depth as the nursery pot

                    **Step 4**: Water thoroughly after planting

                    **Step 5**: Place in location with appropriate sunlight ({})

                    **Step 6**: Water as needed: {}
                    """.format(
                        tree.get('pot_size', '8-10 inches'),
                        tree.get('sunlight_need', 'moderate sunlight'),
                        tree.get('watering', 'regularly')
                    ))
                else:
                    st.markdown("""
                    **Step 1**: Dig a hole 2-3 times wider than the root ball

                    **Step 2**: Remove the plant from container and loosen roots

                    **Step 3**: Place tree in hole at proper depth

                    **Step 4**: Fill hole with soil and water thoroughly

                    **Step 5**: Add mulch around base (keep away from trunk)

                    **Step 6**: Stake if necessary for support
                    """)
        except Exception as e:
            st.warning(f"Planting guide not available for {tree['name']}. Showing general guidelines.")
            if is_balcony:
                st.markdown("""
                **General Balcony Plant Care:**
                1. Use a pot with drainage holes
                2. Use quality potting mix
                3. Water when top soil feels dry
                4. Ensure adequate sunlight
                5. Fertilize monthly during growing season
                """)
            else:
                st.markdown("""
                **General Tree Planting:**
                1. Dig appropriate sized hole
                2. Plant at correct depth
                3. Water deeply
                4. Mulch around base
                5. Stake if needed
                """)

        # Maintenance calendar
        st.subheader("Maintenance Calendar")

        try:
            maintenance = get_maintenance_guide(tree['name'])

            if maintenance and len(maintenance) > 0:
                # Create tabs for seasons
                tabs = st.tabs(["Spring", "Summer", "Monsoon", "Winter"])

                for i, season in enumerate(["Spring", "Summer", "Monsoon", "Winter"]):
                    with tabs[i]:
                        if season in maintenance:
                            for task in maintenance[season]:
                                st.markdown(f"- {task}")
                        else:
                            st.write("No specific maintenance tasks for this season.")
            else:
                # Generic maintenance if specific guide not available
                st.info("Showing general maintenance guidelines:")
                tabs = st.tabs(["Spring", "Summer", "Monsoon", "Winter"])

                with tabs[0]:  # Spring
                    if is_balcony:
                        st.markdown("""
                        - Start regular watering schedule
                        - Apply balanced fertilizer
                        - Prune dead leaves
                        - Check for pests
                        """)
                    else:
                        st.markdown("""
                        - Inspect for winter damage
                        - Apply fertilizer
                        - Prune as needed
                        - Check for pests and diseases
                        """)

                with tabs[1]:  # Summer
                    if is_balcony:
                        st.markdown("""
                        - Water more frequently in heat
                        - Provide shade if needed
                        - Watch for leaf burn
                        - Continue pest monitoring
                        """)
                    else:
                        st.markdown("""
                        - Deep water during dry spells
                        - Maintain mulch layer
                        - Watch for drought stress
                        - Monitor for pests
                        """)

                with tabs[2]:  # Monsoon
                    if is_balcony:
                        st.markdown("""
                        - Reduce watering frequency
                        - Ensure good drainage
                        - Protect from excess rain if needed
                        - Watch for fungal issues
                        """)
                    else:
                        st.markdown("""
                        - Ensure proper drainage
                        - Watch for fungal diseases
                        - Support if needed in wind
                        - Minimal watering needed
                        """)

                with tabs[3]:  # Winter
                    if is_balcony:
                        st.markdown("""
                        - Reduce watering
                        - Protect from frost if needed
                        - Move indoors if frost-sensitive
                        - Reduce fertilizer
                        """)
                    else:
                        st.markdown("""
                        - Water occasionally if dry
                        - Protect young trees from frost
                        - Avoid pruning
                        - Plan spring activities
                        """)
        except Exception as e:
            st.info("Maintenance calendar not available. Follow general care instructions above.")

        # Add to planted trees
        st.subheader("Track This Plant")
        # --- CREATE tree_to_track SAFELY ---
        import datetime

        # Ensure planted_trees exists
        if "planted_trees" not in st.session_state:
            st.session_state.planted_trees = []

        # Ensure we have a 'tree' object from the recommendation or selection
        # If not, avoid breaking the app
        if 'tree' not in locals() and 'tree' not in st.session_state:
            st.warning("No tree selected to track.")
        else:
            selected_tree = tree if 'tree' in locals() else st.session_state.tree

            # Create a safe tracking object
            tree_to_track = {
                "name": selected_tree.get("name", "Unknown"),
                "species": selected_tree.get("species", "Unknown"),
                "planted_on": datetime.date.today().isoformat(),
                "health_status": "Healthy",
                "location": st.session_state.get("location", "Not Set"),
                "notes": ""
            }

        # Inside "Track This Tree" / "Add to My Garden" button:
        if st.button("Add to My Garden"):
            # ... existing code ...
            st.session_state.planted_trees.append(tree_to_track)

            # NEW: Add these lines
            st.session_state.user_profile['trees_planted'] += 1
            add_xp(50, f"Planted {tree['name']}!")
            check_and_award_badges()

            st.success(f"✅ {tree['name']} added to your tracked plants. View in 'Impact Tracker'.")
            # Add current date and initial status
            import datetime

            tree_to_track = tree.copy()
            tree_to_track['planted_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            tree_to_track['status'] = "Newly Planted"
            tree_to_track['health'] = "Good"

            st.session_state.planted_trees.append(tree_to_track)
            st.success(f"✅ {tree['name']} added to your tracked plants. View in 'Impact Tracker'.")
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

            # Inside "Update Status" button:
            if st.button("Update Status"):
                for tree in st.session_state.planted_trees:
                    if tree['name'] == tree_to_update:
                        tree['status'] = new_status
                        tree['health'] = new_health
                        break

                # NEW: Add these lines
                add_xp(20, "Updated plant status!")
                check_and_award_badges()

                st.success(f"Status updated for {tree_to_update}")
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
        # Community page
        # Community Page


elif page == "Community":
    display_community_feed()


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
    "Tree Plantation Planner | A data-driven approach to smarter afforestation"
)
