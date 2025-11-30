import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import uuid
import os
from dotenv import load_dotenv
from PIL import Image
import io
import json

# existing imports from your project
from community import initialize_community, display_community_feed
import geopy
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# local modules
from tree_data import get_tree_data, get_tree_details, get_balcony_plants_data
from recommendation import get_recommendations, get_balcony_recommendations

# Optional imports with fallbacks
try:
    from climate_data import get_climate_data
except Exception:
    def get_climate_data(lat, lon):
        return {"avg_temp": 28, "annual_rainfall": 800, "humidity": 60, "climate_zone": "Tropical"}

try:
    from soil_data import get_soil_types, get_soil_data
except Exception:
    def get_soil_data(lat, lon):
        return {"soil_type": "Loamy", "ph_level": 6.8, "drainage": "Good", "nutrient_level": "Medium"}

try:
    from impact_calculator import calculate_impact
except Exception:
    def calculate_impact(plants):
        return {"carbon_sequestered": max(0.1, len(plants) * 22.0), "oxygen_produced": max(0.1, len(plants) * 1.2),
                "pollutants_removed": max(0.1, len(plants) * 5.0)}

try:
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
except Exception:
    def display_tree_svg():
        pass


    def get_planting_guide(name):
        return []


    def get_maintenance_guide(name):
        return {}


    def initialize_user_profile():
        st.session_state.setdefault('user_profile', {"trees_planted": 0})


    def add_xp(a, b):
        pass


    def calculate_green_score():
        return 0


    def display_profile_sidebar():
        pass


    def update_streak():
        pass


    def check_and_award_badges():
        pass

# Load environment
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

st.set_page_config(page_title="AirCare - Tree & Air Quality Planner", page_icon="🌳", layout="wide")

# ===========================
# AIR QUALITY FUNCTIONS
# ===========================

# Plant effectiveness database (sq ft coverage per plant)
PLANT_AIR_DATA = {
    "Areca Palm": {
        "effectiveness": 120,
        "removes": ["Formaldehyde", "Xylene", "Toluene"],
        "pm_reduction": 30,
        "care": "Medium"
    },
    "Snake Plant": {
        "effectiveness": 40,
        "removes": ["Formaldehyde", "Benzene", "CO"],
        "pm_reduction": 18,
        "care": "Very Easy"
    },
    "Peace Lily": {
        "effectiveness": 50,
        "removes": ["Ammonia", "Benzene", "Formaldehyde", "TCE"],
        "pm_reduction": 25,
        "care": "Easy"
    },
    "Spider Plant": {
        "effectiveness": 50,
        "removes": ["CO", "Formaldehyde", "Xylene"],
        "pm_reduction": 20,
        "care": "Very Easy"
    },
    "Rubber Plant": {
        "effectiveness": 100,
        "removes": ["Formaldehyde"],
        "pm_reduction": 35,
        "care": "Easy"
    },
    "Boston Fern": {
        "effectiveness": 60,
        "removes": ["Formaldehyde", "Xylene"],
        "pm_reduction": 28,
        "care": "Medium"
    },
    "Money Plant": {
        "effectiveness": 60,
        "removes": ["Formaldehyde", "Benzene", "Xylene", "Toluene"],
        "pm_reduction": 22,
        "care": "Very Easy"
    },
    "Neem": {
        "effectiveness": 200,
        "removes": ["PM2.5", "PM10", "Natural purifier"],
        "pm_reduction": 45,
        "care": "Low"
    }
}


def fetch_aqi_openweather(lat, lon, api_key):
    """Fetch real-time AQI data from OpenWeatherMap"""
    if not api_key:
        return None
    try:
        url = "http://api.openweathermap.org/data/2.5/air_pollution"
        params = {"lat": lat, "lon": lon, "appid": api_key}
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        if 'list' in data and data['list']:
            rec = data['list'][0]
            return {
                "aqi_index": rec.get('main', {}).get('aqi'),
                "components": rec.get('components', {}),
                "dt": rec.get('dt'),
                "timestamp": datetime.datetime.fromtimestamp(rec.get('dt', 0))
            }
    except Exception as e:
        st.error(f"⚠️ AQI fetch failed: {e}")
    return None


def aqi_to_label(aqi_index):
    """Convert AQI index to readable label"""
    map_ = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
    return map_.get(aqi_index, "Unknown")


def aqi_to_color(aqi_index):
    """Get color for AQI visualization"""
    colors = {1: "green", 2: "lightgreen", 3: "yellow", 4: "orange", 5: "red"}
    return colors.get(aqi_index, "gray")


def get_aqi_action_plan(aqi_index, pm25, location_data):
    """Generate personalized daily action plan based on AQI"""
    actions = []

    if aqi_index >= 5:
        actions = [
            "🚪 Stay indoors as much as possible",
            "🪟 Keep all windows and doors closed",
            "💧 Water your indoor plants - they help filter air",
            "😷 Wear N95/N99 mask if you must go outside",
            "🌱 Place air-purifying plants near sleeping area",
            "⚕️ Avoid outdoor exercise completely",
            "🧒 Keep children and elderly indoors"
        ]
    elif aqi_index >= 4:
        actions = [
            "⏰ Limit outdoor time to essential activities only",
            "🪟 Keep windows closed during peak pollution hours (6-10 AM, 5-9 PM)",
            "💧 Water your plants today - especially Areca Palm and Snake Plant",
            "😷 Wear mask outdoors",
            "🏃 Postpone outdoor exercise",
            "🌿 Check your balcony plants - they're working hard today"
        ]
    elif aqi_index >= 3:
        actions = [
            "⚠️ Sensitive individuals should limit prolonged outdoor activities",
            "🪟 Ventilate during midday when AQI is typically better",
            "💧 Ensure plants are well-watered",
            "🏃 Exercise early morning or evening",
            "🌱 Good day to add more air-purifying plants"
        ]
    else:
        actions = [
            "✅ Air quality is acceptable today",
            "🪟 Safe to ventilate your home",
            "🏃 Great day for outdoor activities",
            "🌱 Perfect time to plant new saplings",
            "💧 Regular plant care routine"
        ]

    return actions


def recommend_plants_by_aqi(pm25, aqi_index):
    """Recommend specific plants based on current pollution levels"""
    if pm25 and pm25 > 50:
        return [
            {"name": "Areca Palm", "reason": "Excellent PM2.5 reducer (30% reduction)"},
            {"name": "Boston Fern", "reason": "Great for particulate matter"},
            {"name": "Rubber Plant", "reason": "Large leaves trap dust"},
            {"name": "Neem", "reason": "Natural air purifier (outdoor)"}
        ]
    elif pm25 and pm25 > 25:
        return [
            {"name": "Snake Plant", "reason": "Removes formaldehyde & benzene"},
            {"name": "Spider Plant", "reason": "Absorbs CO and toxins"},
            {"name": "Peace Lily", "reason": "Filters multiple pollutants"}
        ]
    else:
        return [
            {"name": "Snake Plant", "reason": "Low maintenance, 24/7 oxygen"},
            {"name": "Money Plant", "reason": "Easy care, good air cleaner"},
            {"name": "Spider Plant", "reason": "Hardy and effective"}
        ]


def calc_plants_needed(room_sqft, plant_name):
    """Calculate number of plants needed for a room"""
    plant_data = PLANT_AIR_DATA.get(plant_name, {"effectiveness": 50})
    base = plant_data["effectiveness"]
    return int(np.ceil(room_sqft / base))


def calculate_home_air_score(answers):
    """Calculate 0-100 home air health score"""
    score = 100

    if answers.get('gas_cooking') == "Yes":
        score -= 20

    if answers.get('smoking') == "Yes":
        score -= 30

    vent = answers.get('ventilation', 'Rarely')
    if vent == "Daily":
        score += 5
    elif vent == "Rarely":
        score -= 20
    else:
        score -= 10

    plant_count = answers.get('plant_count', 0)
    score += min(10, plant_count * 2)

    if answers.get('purifier') == "Yes":
        score += 10
    else:
        score -= 10

    if answers.get('carpets') == "Yes":
        score -= 10

    if answers.get('ac_filter') == "Never/Rarely":
        score -= 15

    return max(0, min(100, score))


def analyze_plant_image(img_bytes):
    """Simple heuristic plant health analysis"""
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_small = img.resize((200, 200))
        arr = np.array(img_small)

        r, g, b = arr[:, :, 0].astype(float), arr[:, :, 1].astype(float), arr[:, :, 2].astype(float)

        green_mask = (g > r * 1.05) & (g > b * 1.05) & (g > 50)
        green_ratio = green_mask.sum() / (arr.shape[0] * arr.shape[1])

        brown_mask = (r > g * 1.05) & (r > b * 1.05) & (r > 80) & (g < 150)
        brown_ratio = brown_mask.sum() / (arr.shape[0] * arr.shape[1])

        yellow_mask = (r > 150) & (g > 150) & (b < 100)
        yellow_ratio = yellow_mask.sum() / (arr.shape[0] * arr.shape[1])

        gray = np.mean(arr, axis=2)
        contrast = gray.std()
        dusty = contrast < 30

        brightness = np.mean(gray)

        return {
            "green_ratio": float(green_ratio),
            "brown_ratio": float(brown_ratio),
            "yellow_ratio": float(yellow_ratio),
            "contrast": float(contrast),
            "brightness": float(brightness),
            "dusty": bool(dusty)
        }
    except Exception as e:
        return {"error": str(e)}


def diagnose_plant_health(analysis):
    """Generate diagnosis from image analysis"""
    issues = []
    recommendations = []

    if 'error' in analysis:
        return ["Error analyzing image"], ["Try uploading a clearer photo"]

    green = analysis['green_ratio']
    brown = analysis['brown_ratio']
    yellow = analysis['yellow_ratio']
    dusty = analysis['dusty']
    brightness = analysis['brightness']

    if green < 0.20:
        issues.append("⚠️ Low green coverage - plant may be severely stressed or dying")
        recommendations.append("Check soil moisture, lighting, and recent care history")
    elif green < 0.35:
        issues.append("⚠️ Moderate stress detected")
        recommendations.append("Review watering schedule and light exposure")

    if brown > 0.08:
        issues.append("🟤 Significant browning detected")
        recommendations.append("Possible causes: overwatering, root rot, sunburn, or pest damage")
        recommendations.append("Check for: mushy roots, burnt leaf edges, tiny insects")

    if yellow > 0.05:
        issues.append("🟡 Yellowing detected (chlorosis)")
        recommendations.append("Likely nitrogen deficiency - add balanced fertilizer")
        recommendations.append("Could also indicate overwatering or poor drainage")

    if dusty:
        issues.append("💨 Heavy dust accumulation detected")
        recommendations.append("Wipe leaves gently with damp cloth")
        recommendations.append("Dust blocks sunlight and clogs pores")

    if brightness < 80:
        issues.append("🌑 Very dark image - may indicate low light conditions")
        recommendations.append("Move plant to brighter location if possible")

    if dusty or brown > 0.05:
        recommendations.append("🏭 In high pollution areas:")
        recommendations.append("• Clean leaves weekly")
        recommendations.append("• Increase watering slightly (plants work harder)")
        recommendations.append("• Check soil pH monthly")

    if len(issues) == 0:
        issues.append("✅ Plant appears healthy!")
        recommendations.append("Continue current care routine")
        recommendations.append("Monitor weekly for any changes")

    return issues, recommendations


# ===========================
# Initialize session state
# ===========================
def init_session_state():
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
        'watering_logs': {},
        'plant_photos': {},
        'care_reminders': {},
        'last_aqi': None,
        'aqi_history': [],
        'home_air_score': None,
        'green_shield_data': {}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session_state()

if 'user_profile' not in st.session_state:
    initialize_user_profile()
    initialize_community()
    update_streak()


# ===========================
# Navigation
# ===========================
def navigate_to(page_name):
    st.session_state.current_page = page_name
    st.rerun()


if 'navigate_to' in st.session_state and st.session_state.navigate_to:
    st.session_state.current_page = st.session_state.navigate_to
    st.session_state.navigate_to = None

# ===========================
# Sidebar Navigation
# ===========================
page_options = [
    "Home",
    "🌫️ AQI Dashboard",
    "Tree Recommendations",
    "Planting Guide",
    "Plant Care Tracker",
    "🧮 Air Calculator",
    "🏠 Home Air Score",
    "🩺 Plant Doctor",
    "Impact Tracker",
    "Community",
    "About"
]

with st.sidebar:
    st.markdown(f"### 📍 Current: *{st.session_state.current_page}*")
    st.markdown("---")
    for page in page_options:
        if st.button(page, key=f"nav_{page}", use_container_width=True):
            navigate_to(page)

display_profile_sidebar()
display_tree_svg()


# ===========================
# Utility Functions
# ===========================
def ensure_tree_has_fields(tree):
    """Ensure tree object has all required fields"""
    defaults = {
        'id': str(uuid.uuid4()),
        'status': 'Newly Planted',
        'health': 'Good',
        'planted_date': datetime.datetime.now().strftime("%Y-m-%d"),
        'name': 'Unknown Plant',
        'purposes': [],
        'environmental_benefits': 'N/A',
        'benefits': 'N/A'  # Added from TPP.py
    }
    for k, v in defaults.items():
        if k not in tree:
            tree[k] = v
    return tree


# ===========================
# HOME PAGE
# ===========================
if st.session_state.current_page == "Home":
    st.title("🌳 AirCare - Smart Tree & Air Quality Planner")

    if st.session_state.location and OPENWEATHER_API_KEY:
        lat = st.session_state.location['latitude']
        lon = st.session_state.location['longitude']
        aqi = fetch_aqi_openweather(lat, lon, OPENWEATHER_API_KEY)
        if aqi:
            aqi_label = aqi_to_label(aqi['aqi_index'])
            aqi_color = aqi_to_color(aqi['aqi_index'])
            st.markdown(f"""
            <div style='background-color: {aqi_color}; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <h3 style='margin: 0; color: white;'>Current Air Quality: {aqi_label}</h3>
                <p style='margin: 5px 0 0 0; color: white;'>PM2.5: {aqi['components'].get('pm2_5', 'N/A')} µg/m³</p>
            </div>
            """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🌍 Why Plant Strategically?")
        st.markdown("""
        - 🌱 Higher survival rates
        - 🌫️ **Better air quality improvement**
        - 🌳 Enhanced biodiversity
        - ♻️ Carbon sequestration
        """)

        st.subheader("🏡 Select Your Space")
        planting_mode = st.radio(
            "Where are you planting?",
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
                st.session_state.sunlight_hours = st.slider("Daily sunlight (hours):", 0, 12, 6)
                st.session_state.planting_purpose = st.multiselect(
                    "Your goals:",
                    ["Air Purification", "Edible (Herbs/Vegetables)", "Aesthetic/Decor",
                     "Low Maintenance", "Medicinal", "Stress Relief"],
                    default=["Air Purification", "Low Maintenance"]
                )
        else:
            st.session_state.is_balcony_mode = False
            st.info("🌳 Outdoor mode activated!")

        st.subheader("📍 Enter Location")
        location_method = st.radio(
            "Choose method:",
            ["Search by address", "Use current location"]
        )

        if location_method == "Search by address":
            address = st.text_input("Enter address, city, or region:")
            if st.button("🔍 Search Location", type="primary"):
                try:
                    geolocator = Nominatim(user_agent="aircare_planner")
                    location = geolocator.geocode(address)
                    if location:
                        st.session_state.location = {
                            "address": location.address,
                            "latitude": location.latitude,
                            "longitude": location.longitude
                        }
                        st.success(f"✅ Found: {location.address}")
                        st.session_state.climate_data = get_climate_data(location.latitude, location.longitude)
                        st.session_state.soil_data = get_soil_data(location.latitude, location.longitude)

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

                        add_xp(10, "Got recommendations!")
                        st.session_state.navigate_to = "Tree Recommendations"
                        st.rerun()
                    else:
                        st.error("Location not found")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("Click to use device location")
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
                            alert('Enable location permissions');
                        },
                        { enableHighAccuracy: true, timeout: 10000 }
                    );
                }
                getLocation();
                </script>
                """
                components.html(js, height=0)

    with col2:
        st.subheader("💡 Did You Know?")
        st.markdown("""
        - 50%+ planted trees die within years
        - Wrong trees deplete groundwater
        - **Right plants reduce indoor pollution by 60%**
        - **Indoor plants remove VOCs & PM2.5**
        """)

        st.subheader("🚀 New Features!")
        st.markdown("""
        - 🌫️ Real-time AQI monitoring
        - 🏠 Home air health score
        - 🩺 AI plant doctor
        - 🧮 Smart plant calculator
        - 💚 Green shield tracker
        """)

query_params = st.query_params
if 'lat' in query_params and 'lon' in query_params:
    try:
        lat = float(query_params['lat'])
        lon = float(query_params['lon'])
        geolocator = Nominatim(user_agent="aircare_planner")
        location = geolocator.reverse(f"{lat}, {lon}")
        st.session_state.location = {
            "address": location.address if location else f"{lat},{lon}",
            "latitude": lat,
            "longitude": lon
        }
        st.session_state.climate_data = get_climate_data(lat, lon)
        st.session_state.soil_data = get_soil_data(lat, lon)

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

        st.query_params.clear()
        st.session_state.current_page = "Tree Recommendations"
        st.rerun()
    except Exception as e:
        st.error(f"Location error: {e}")

# ===========================
# AQI DASHBOARD (KILLER FEATURE #1)
# ===========================
elif st.session_state.current_page == "🌫️ AQI Dashboard":
    st.header("🌫️ Real-Time Air Quality Dashboard")

    if st.session_state.location is None:
        st.warning("⚠️ Set location on Home page first")
        if st.button("← Go to Home", type="primary"):
            navigate_to("Home")
    else:
        lat = st.session_state.location['latitude']
        lon = st.session_state.location['longitude']

        st.subheader(f"📍 {st.session_state.location['address']}")

        if not OPENWEATHER_API_KEY:
            st.error("🔑 Add OPENWEATHER_API_KEY to .env file")
            st.info("Get free API key at: https://openweathermap.org/api")
        else:
            with st.spinner("Fetching air quality data..."):
                aqi = fetch_aqi_openweather(lat, lon, OPENWEATHER_API_KEY)

            if aqi:
                st.session_state.last_aqi = aqi

                label = aqi_to_label(aqi['aqi_index'])
                color = aqi_to_color(aqi['aqi_index'])
                comps = aqi['components']

                st.markdown(f"""
                <div style='background-color: {color}; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;'>
                    <h1 style='color: white; margin: 0;'>{label}</h1>
                    <h3 style='color: white; margin: 10px 0 0 0;'>AQI Index: {aqi['aqi_index']}/5</h3>
                    <p style='color: white; margin: 5px 0 0 0;'>Updated: {aqi['timestamp'].strftime('%I:%M %p')}</p>
                </div>
                """, unsafe_allow_html=True)

                st.subheader("🔬 Pollutant Levels")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("PM2.5", f"{comps.get('pm2_5', 0):.1f} µg/m³")
                col2.metric("PM10", f"{comps.get('pm10', 0):.1f} µg/m³")
                col3.metric("NO₂", f"{comps.get('no2', 0):.1f} µg/m³")
                col4.metric("O₃", f"{comps.get('o3', 0):.1f} µg/m³")

                st.markdown("---")
                st.subheader("📋 YOUR PERSONALIZED ACTION PLAN FOR TODAY")

                actions = get_aqi_action_plan(aqi['aqi_index'], comps.get('pm2_5'), st.session_state.location)
                for action in actions:
                    st.markdown(f"**{action}**")

                st.markdown("---")
                st.subheader("🌱 Plants Recommended for Today's Air Quality")

                plant_recs = recommend_plants_by_aqi(comps.get('pm2_5'), aqi['aqi_index'])
                rec_cols = st.columns(len(plant_recs))
                for idx, rec in enumerate(plant_recs):
                    with rec_cols[idx]:
                        st.markdown(f"**{rec['name']}**")
                        st.caption(rec['reason'])
                        if st.button(f"Add {rec['name']}", key=f"add_plant_{idx}"):
                            st.success(f"✅ {rec['name']} added!")

                st.markdown("---")
                st.subheader("⚕️ Health Recommendations")

                if aqi['aqi_index'] >= 4:
                    st.error("⚠️ Air quality is harmful")
                    st.markdown("""
                    **Who is at risk:**
                    - Children and elderly
                    - People with asthma/COPD
                    - Heart disease patients
                    """)
                elif aqi['aqi_index'] == 3:
                    st.warning("⚠️ Moderate air quality")
                else:
                    st.success("✅ Air quality is acceptable")

                if st.session_state.planted_trees:
                    st.markdown("---")
                    st.subheader("🛡️ YOUR GREEN SHIELD TODAY")

                    total_plants = len(st.session_state.planted_trees)
                    estimated_pm_filtered = total_plants * 2.5
                    estimated_voc_filtered = total_plants * 15

                    shield_col1, shield_col2, shield_col3 = st.columns(3)
                    shield_col1.metric("🌿 Active Plants", total_plants)
                    shield_col2.metric("💨 Est. PM2.5 Filtered", f"{estimated_pm_filtered:.1f}g today")
                    shield_col3.metric("🧪 Est. VOCs Removed", f"{estimated_voc_filtered:.0f}µg today")

                    st.info("💡 Your plants are actively cleaning your air!")
            else:
                st.error("Unable to fetch AQI data")

# ===========================
# Tree Recommendations
# (MERGED FROM TPP.py for more detail)
# ===========================
elif st.session_state.current_page == "Tree Recommendations":
    st.header("🌱 Plant Recommendations")

    if st.session_state.location is None:
        st.warning("⚠ Please set your location on the Home page first.")
        if st.button("← Go to Home", type="primary"):
            navigate_to("Home")
    else:
        # Show mode badge
        if st.session_state.is_balcony_mode:
            st.success("🪴 *Balcony Mode* - Space-efficient plants")
        else:
            st.success("🌳 *Outdoor Mode* - Ground planting trees")

        st.subheader(f"📍 {st.session_state.location['address']}")

        # Display climate and soil
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Climate Conditions")
            if st.session_state.climate_data:
                st.write(f"🌡 Avg Temperature: {st.session_state.climate_data['avg_temp']}°C")
                st.write(f"🌧 Annual Rainfall: {st.session_state.climate_data['annual_rainfall']} mm")
                st.write(f"💧 Humidity: {st.session_state.climate_data.get('humidity', 'N/A')}%")
                st.write(f"🌍 Climate Zone: {st.session_state.climate_data['climate_zone']}")

        with col2:
            st.subheader("Soil Conditions")
            if st.session_state.soil_data:
                st.write(f"🪨 Soil Type: {st.session_state.soil_data['soil_type']}")
                st.write(f"⚗ pH Level: {st.session_state.soil_data['ph_level']}")
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
                                    st.write(f"*Scientific*: {item.get('scientific_name', 'N/A')}")
                                    st.write(f"*Space*: {item.get('space_required', 'N/A')}")
                                    st.write(f"*Sunlight*: {item.get('sunlight_need', 'N/A')}")
                                    st.write(f"*Watering*: {item.get('watering', 'N/A')}")
                                    st.write(f"*Difficulty*: {item.get('care_difficulty', 'N/A')}")
                                    st.write(f"*Benefits*: {item.get('benefits', 'N/A')}")
                                else:
                                    st.subheader(f"🌳 {item['name']}")
                                    st.write(f"*Scientific*: {item.get('scientific_name', 'N/A')}")
                                    st.write(f"*Growth Rate*: {item.get('growth_rate', 'N/A')}")
                                    st.write(f"*Benefits*: {item.get('environmental_benefits', 'N/A')}")

                                if st.button(f"Select {item['name']}", key=f"select_{i}_{j}"):
                                    st.session_state.selected_tree = item
                                    add_xp(5, f"Selected {item['name']}")
                                    navigate_to("Planting Guide")
        else:
            st.info("No recommendations yet. Return to Home to set location.")

# ===========================
# Planting Guide
# (MERGED FROM TPP.py for more detail)
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
# Plant Care Tracker
# (MERGED FROM TPP.py for more detail)
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
# AIR CALCULATOR (KILLER FEATURE #3)
# ===========================
elif st.session_state.current_page == "🧮 Air Calculator":
    st.header("🧮 Indoor Air Purifier Calculator")

    room_sqft = st.number_input("Room area (square feet):", min_value=10, max_value=2000, value=150, step=10)
    plant_choice = st.selectbox("Choose plant type:", list(PLANT_AIR_DATA.keys()))

    if st.button("🧮 Calculate", type="primary"):
        needed = calc_plants_needed(room_sqft, plant_choice)
        plant_info = PLANT_AIR_DATA[plant_choice]

        st.success(f"### 🌱 You need {needed} x {plant_choice}")
        st.markdown(f"**Coverage:** {plant_info['effectiveness']} sq ft per plant")
        st.markdown(f"**Removes:** {', '.join(plant_info['removes'])}")
        st.markdown(f"**PM Reduction:** Up to {plant_info['pm_reduction']}%")
        st.markdown(f"**Care Level:** {plant_info['care']}")

        avg_cost_per_plant = 300
        total_cost = needed * avg_cost_per_plant
        st.markdown(f"**Estimated Cost:** ₹{total_cost:,}")

    st.markdown("---")
    st.subheader("📊 Plant Comparison")

    comparison_data = []
    for name, data in PLANT_AIR_DATA.items():
        comparison_data.append({
            "Plant": name,
            "Coverage (sq ft)": data['effectiveness'],
            "PM Reduction (%)": data['pm_reduction'],
            "Care": data['care'],
            "Plants Needed": calc_plants_needed(room_sqft, name)
        })

    df = pd.DataFrame(comparison_data).sort_values("Plants Needed")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ===========================
# HOME AIR SCORE (KILLER FEATURE #4)
# ===========================
elif st.session_state.current_page == "🏠 Home Air Score":
    st.header("🏠 Home Air Health Score")

    with st.form("home_air_form"):
        q1 = st.radio("Cook with gas indoors?", ["Yes", "No"], index=1)
        q2 = st.radio("Smoke indoors?", ["Yes", "No"], index=1)
        q3 = st.radio("Have carpets?", ["Yes", "No"], index=0)
        q4 = st.radio("Ventilate how often?", ["Daily", "Few times a week", "Rarely"], index=0)
        q5 = st.number_input("Number of plants?", min_value=0, max_value=100, value=2)
        q6 = st.radio("Use air purifier?", ["Yes", "No"], index=1)
        q7 = st.radio("Clean AC filters?", ["Monthly", "Every 3 months", "Every 6 months", "Never/Rarely"], index=1)

        submitted = st.form_submit_button("🧮 Calculate Score", type="primary")

    if submitted:
        answers = {
            'gas_cooking': q1,
            'smoking': q2,
            'carpets': q3,
            'ventilation': q4,
            'plant_count': q5,
            'purifier': q6,
            'ac_filter': q7
        }

        score = calculate_home_air_score(answers)

        if score >= 80:
            color, grade = "green", "Excellent 🌟"
        elif score >= 60:
            color, grade = "lightgreen", "Good ✅"
        elif score >= 40:
            color, grade = "orange", "Fair ⚠️"
        else:
            color, grade = "red", "Poor ❌"

        st.markdown(f"""
        <div style='background-color: {color}; padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0;'>
            <h1 style='color: white; margin: 0;'>{score}/100</h1>
            <h2 style='color: white; margin: 10px 0 0 0;'>{grade}</h2>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📋 Recommendations")

        if answers['gas_cooking'] == "Yes":
            st.markdown("**Install kitchen exhaust fan**")
        if answers['smoking'] == "Yes":
            st.markdown("**⚠️ CRITICAL: Stop smoking indoors**")
        if answers['ventilation'] == "Rarely":
            st.markdown("**Open windows 15-30 min daily**")
        if answers['plant_count'] < 5:
            st.markdown(f"**Add {5 - answers['plant_count']} more plants**")
        if answers['purifier'] == "No" and score < 60:
            st.markdown("**Consider HEPA air purifier**")

# ===========================
# PLANT DOCTOR (KILLER FEATURE #5)
# ===========================
elif st.session_state.current_page == "🩺 Plant Doctor":
    st.header("🩺 AI Plant Doctor")

    uploaded = st.file_uploader("📸 Upload plant photo", type=['jpg', 'jpeg', 'png'])

    if uploaded:
        bytes_data = uploaded.getvalue()
        st.image(bytes_data, use_column_width=True)

        if st.button("🔬 Analyze", type="primary"):
            with st.spinner("Analyzing..."):
                analysis = analyze_plant_image(bytes_data)
                issues, recommendations = diagnose_plant_health(analysis)

            st.subheader("🔍 Results")

            if 'error' not in analysis:
                col1, col2, col3 = st.columns(3)
                col1.metric("🟢 Green", f"{analysis['green_ratio'] * 100:.1f}%")
                col2.metric("🟤 Brown", f"{analysis['brown_ratio'] * 100:.1f}%")
                col3.metric("💨 Dust", "High" if analysis['dusty'] else "Normal")

            st.subheader("⚠️ Issues")
            for issue in issues:
                st.markdown(f"- {issue}")

            st.subheader("💡 Recommendations")
            for rec in recommendations:
                st.markdown(f"- {rec}")

# ===========================
# Impact Tracker
# (MERGED FROM TPP.py for more detail)
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
# Community
# ===========================
elif st.session_state.current_page == "Community":
    display_community_feed()

# ===========================
# About
# (MERGED FROM TPP.py for more detail)
# ===========================
elif st.session_state.current_page == "About":
    st.header("About the Tree Plantation Planner")

    # Project Overview
    st.subheader("🌍 Project Objective")
    st.markdown("""
    The Tree Plantation Planner is designed to guide people in making smarter planting choices. 
    By recommending the right trees and plants for the right places, it ensures that plantation efforts actually 
    benefit the environment, improve air quality, and support biodiversity—whether you're planting in a forest, 
    backyard, or urban balcony.
    """)

    # Why We Created This
    st.subheader("💡 Why We Created This Tool")
    st.markdown("""
    Across the world, large-scale afforestation efforts are undertaken to fight climate change, 
    improve air quality, and restore ecosystems. However, many of these efforts fail to produce 
    real impact because:

    - 🌱 Trees are planted randomly without considering local soil, climate, and biodiversity
    - ☠ High mortality rates leave behind empty land instead of thriving forests
    - ⚠ Inappropriate tree choices damage ecosystems rather than restoring them
    - 🏙 Urban dwellers lack guidance on space-efficient planting options

    This project aims to fix these problems by helping individuals, communities, and policymakers 
    choose the right plants for the right places—from large outdoor trees to compact balcony plants.
    """)

    # NEW: Urban & Balcony Plantation Section
    st.subheader("🪴 Urban & Balcony Plantation: A Growing Movement")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### Why Balcony Planting Matters

        With rapid urbanization, millions of people live in apartments without access to traditional gardens. 
        Yet urban green spaces are crucial for:

        - *Air Quality*: Indoor plants remove toxins like formaldehyde, benzene, and CO₂
        - *Mental Health*: Studies show plants reduce stress and improve mood by 30%
        - *Food Security*: Growing herbs and vegetables reduces carbon footprint from transportation
        - *Urban Heat Islands*: Balcony gardens can reduce indoor temperatures by 3-5°C
        - *Biodiversity*: Even small plants provide habitats for pollinators like bees and butterflies

        #### The Urban Challenge

        Urban dwellers face unique constraints:
        - Limited space (often <5 m²)
        - Restricted sunlight (2-6 hours daily)
        - Watering challenges
        - Lack of soil/gardening knowledge

        Our balcony mode solves this by recommending:
        ✅ *Space-efficient plants* that thrive in pots  
        ✅ *Low-maintenance options* for busy lifestyles  
        ✅ *Sunlight-adapted species* for shaded balconies  
        ✅ *Edible & medicinal plants* for practical benefits  
        """)

    with col2:
        st.markdown("""
        #### Balcony Planting by the Numbers

        🌿 *Global Impact*:
        - 55% of world population lives in urban areas (UN, 2023)
        - 80% lack access to traditional gardens
        - Urban balcony gardens can offset 2-5 kg CO₂/year per plant

        🇮🇳 *India-Specific Data*:
        - 35% of Indians live in urban areas (Census 2021)
        - Mumbai & Delhi have <10m² green space per capita (WHO recommends 50m²)
        - Air pollution causes 1.67 million deaths annually (Lancet, 2022)

        🌱 *Success Stories*:
        - Singapore's "City in a Garden" increased urban greenery to 47%
        - Tokyo's balcony gardens reduced AC usage by 20%
        - Bangalore's "Balcony Garden Movement" has 50,000+ participants

        #### What You Can Grow

        *Herbs & Vegetables*:  
        Mint, Coriander, Curry Leaves, Tomatoes, Chillies, Spinach

        *Air Purifiers*:  
        Snake Plant, Money Plant, Spider Plant, Peace Lily, Aloe Vera

        *Medicinal*:  
        Tulsi (Holy Basil), Aloe Vera, Brahmi, Ashwagandha

        *Aesthetic*:  
        Jade Plant, Areca Palm, Boston Fern, Rubber Plant
        """)

    # Best Practices for Balcony Gardening
    st.subheader("🌿 Best Practices for Balcony Gardening")

    tab1, tab2, tab3, tab4 = st.tabs(["🪴 Getting Started", "💧 Watering & Care", "🌞 Light Management", "🐛 Pest Control"])

    with tab1:
        st.markdown("""
        #### Setting Up Your Balcony Garden

        *1. Assess Your Space*:
        - Measure available area (length × width)
        - Note sunlight hours (use a sun calculator app)
        - Check balcony direction (North/South/East/West)
        - Consider weight limits (consult building regulations)

        *2. Choose Right Containers*:
        - *Plastic pots*: Lightweight, affordable, retain moisture
        - *Terracotta*: Breathable, good for succulents, heavier
        - *Grow bags*: Space-saving, good drainage, portable
        - *Vertical planters*: Maximize space for herbs

        *3. Soil Mix Recipe*:
        - 40% Cocopeat (moisture retention)
        - 30% Regular soil
        - 20% Compost/vermicompost
        - 10% Perlite or sand (drainage)

        *4. Drainage is Critical*:
        - Ensure pots have 2-3 drainage holes
        - Add 2cm gravel/pebbles at bottom
        - Never let water stagnate

        *5. Start Small*:
        - Begin with 3-5 easy plants (Snake Plant, Mint, Money Plant)
        - Learn watering patterns for 2-3 months
        - Gradually expand your collection
        """)

    with tab2:
        st.markdown("""
        #### Watering & Maintenance Guide

        *Watering Schedule* (India-specific):

        | Season | Frequency | Best Time |
        |--------|-----------|-----------|
        | *Summer* (Mar-Jun) | Daily or twice daily | Early morning (6-8 AM) |
        | *Monsoon* (Jul-Sep) | 2-3 times/week | Check soil first |
        | *Winter* (Nov-Feb) | 3-4 times/week | Mid-morning (10 AM) |

        *The Finger Test*:
        - Insert finger 2cm into soil
        - If dry → water thoroughly
        - If moist → skip watering

        *Fertilizing*:
        - Use organic compost every 3-4 weeks
        - Liquid fertilizer (diluted) every 2 weeks during growing season
        - Avoid over-fertilizing (causes salt buildup)

        *Pruning*:
        - Remove dead/yellow leaves weekly
        - Trim overgrown stems to encourage bushiness
        - Harvest herbs regularly to promote growth

        *Common Mistakes*:
        ❌ Overwatering (leads to root rot)  
        ❌ Using garden soil directly (too heavy, poor drainage)  
        ❌ Ignoring drainage holes  
        ❌ Placing all plants in same light conditions  
        """)

    with tab3:
        st.markdown("""
        #### Optimizing Sunlight

        *Understanding Your Balcony*:

        | Direction | Sunlight | Best Plants |
        |-----------|----------|-------------|
        | *East* | Morning sun (4-6 hrs) | Herbs, Tulsi, Vegetables |
        | *West* | Afternoon sun (4-6 hrs) | Succulents, Aloe, Cacti |
        | *South* | Full sun (8+ hrs) | Tomatoes, Chillies, Sunflowers |
        | *North* | Indirect/low light | Snake Plant, Money Plant, Ferns |

        *Solutions for Low Light*:
        - Use reflective surfaces (white walls, mirrors)
        - Rotate plants weekly for even exposure
        - Choose shade-tolerant species
        - Consider grow lights (LED, 6-8 hours/day)

        *Too Much Sun?*:
        - Use shade cloth (30-50% density)
        - Create temporary shade with curtains
        - Move sensitive plants during peak hours (12-3 PM)
        - Increase watering frequency
        """)

    with tab4:
        st.markdown("""
        #### Natural Pest Control

        *Common Pests*:
        - *Aphids*: Spray with neem oil + water (1:10)
        - *Mealybugs*: Wipe with rubbing alcohol on cotton
        - *Fungus Gnats*: Reduce watering, add sand layer on top
        - *Spider Mites*: Increase humidity, spray with water

        *Organic Solutions*:
        1. *Neem Oil Spray*: 10ml neem oil + 1L water + 2 drops soap
        2. *Garlic Spray*: Crush 10 cloves + 1L water, strain, spray
        3. *Cinnamon Powder*: Sprinkle on soil to prevent fungal growth

        *Prevention*:
        - Inspect plants weekly
        - Quarantine new plants for 2 weeks
        - Keep area clean (remove dead leaves)
        - Avoid overcrowding
        """)

    # Social Impact Section
    st.subheader("🌱 Social & Environmental Impact")

    impact_col1, impact_col2 = st.columns(2)

    with impact_col1:
        st.markdown("""
        #### Community Benefits

        Planting trees and balcony gardens isn't just about filling up empty spaces—it's about making a difference:

        *Environmental*:
        - 🌫 Reduce air pollution by filtering PM2.5 and toxins
        - 🌡 Combat urban heat islands (trees can cool areas by 2-8°C)
        - 💧 Improve water retention and reduce flooding
        - 🦋 Enhance biodiversity by supporting pollinators
        - 🌍 Sequester carbon (a mature tree absorbs 22 kg CO₂/year)

        *Health*:
        - 🫁 Improve respiratory health (WHO: trees reduce asthma by 25%)
        - 🧠 Boost mental wellbeing (greenery reduces stress by 30%)
        - 💪 Encourage outdoor activity and community engagement
        - 🥗 Provide access to fresh, organic produce
        """)

    with impact_col2:
        st.markdown("""
        #### Educational Impact

        *For Children*:
        - Hands-on science learning (photosynthesis, life cycles)
        - Responsibility and patience development
        - Connection to nature in urban settings

        *For Communities*:
        - Shared knowledge through local gardening groups
        - Seed/plant exchanges reducing costs
        - Intergenerational bonding activities

        *Economic*:
        - 💰 Reduce grocery costs (herbs save ₹500-1000/month)
        - 🏠 Increase property value (greenery adds 10-15%)
        - ⚡ Lower energy bills (plants reduce AC usage)
        """)

    # Research & Data Sources
    st.subheader("📚 Research & Data Sources")
    st.markdown("""
    This project is backed by scientific research and real-world data:

    *Climate & Environmental*:
    - 🌍 NASA Climate Change Data – Research on deforestation and afforestation impact
    - 📊 IPCC Climate Reports (2023) – Studies on afforestation as a climate solution
    - 🌳 FAO Report (2023) – Global forest mortality and plantation strategies

    *Urban Forestry & Air Quality*:
    - 🏙 World Health Organization (WHO) – Urban forestry and pollution reduction
    - 🫁 Lancet Planetary Health (2022) – Air pollution and mortality in India
    - 🌿 The Nature Conservancy – Urban tree benefits calculator

    *Balcony & Indoor Gardening*:
    - 🪴 NASA Clean Air Study – Air-purifying plants research
    - 🏡 Journal of Environmental Psychology – Mental health benefits of indoor plants
    - 🌱 Royal Horticultural Society (RHS) – Container gardening best practices

    *India-Specific Data*:
    - 📈 Census of India 2021 – Urbanization statistics
    - 🌆 Ministry of Environment (MoEFCC) – Green India Mission data
    - 🌳 Indian State of Forest Report (FSR 2021) – Tree cover statistics
    """)

    # Call to Action
    st.subheader("🚀 Get Started Today")
    st.markdown("""
    Whether you have acres of land or just a small balcony, every plant makes a difference. 

    *Start Your Journey*:
    1. 🏠 Go to *Home* and select your space type (Outdoor/Balcony)
    2. 📍 Enter your location for personalized recommendations
    3. 🌱 Choose plants that match your space and goals
    4. 📊 Track your impact and watch your garden grow!

    *Join the Movement*:
    - Share your progress in the *Community* tab
    - Inspire others with photos of your plants
    - Learn from fellow gardeners' experiences

    ---

    💚 "The best time to plant a tree was 20 years ago. The second best time is now."  
    – Chinese Proverb
    """)

    # Quick Action Buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🌳 Start Outdoor Planting", type="primary", use_container_width=True):
            st.session_state.is_balcony_mode = False
            navigate_to("Home")

    with col2:
        if st.button("🪴 Start Balcony Garden", type="primary", use_container_width=True):
            st.session_state.is_balcony_mode = True
            navigate_to("Home")

    with col3:
        if st.button("👥 Join Community", type="secondary", use_container_width=True):
            navigate_to("Community")

st.markdown("---")
st.caption("💡 Get free OpenWeatherMap API key at https://openweathermap.org/api")