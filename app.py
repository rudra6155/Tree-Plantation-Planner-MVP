import streamlit as st
import time
import pandas as pd
import numpy as np
import requests
import datetime
import uuid
import os
from dotenv import load_dotenv
from PIL import Image
import io

import db_handler  # <-- ADD THIS LINE
import json
from guardian_dashboard import show_guardian_super_dashboard
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

# Test Firebase connection on startup
if st.button("🧪 Test Firebase Connection (Debug)", key="test_firebase"):
    if db_handler.test_firebase_connection():
        st.success("✅ Firebase connected!")
    else:
        st.error("❌ Firebase connection failed")

def load_user_data_if_logged_in():
    """
    Called on every app run to restore user data from Firebase if already logged in
    """
    if st.session_state.get('logged_in', False) and st.session_state.get('user_id'):
        # User is logged in - check if we need to reload from DB
        if 'planted_trees' not in st.session_state or st.session_state.planted_trees is None:
            try:
                loaded_trees = db_handler.load_planted_trees(st.session_state.user_id)
                if loaded_trees:
                    st.session_state.planted_trees = loaded_trees
                    st.session_state.user_state = "GUARDIAN" if len(loaded_trees) > 0 else "EXPLORER"
            except:
                st.session_state.planted_trees = []
                st.session_state.user_state = "EXPLORER"
def add_plant_to_garden_safe(plant_data):
    """Universal function to add plant with proper initialization"""
    plant = standardize_plant_data(plant_data)

    # Add to session state
    st.session_state.planted_trees.append(plant)

    # Initialize watering logs for this plant
    if plant['id'] not in st.session_state.watering_logs:
        st.session_state.watering_logs[plant['id']] = []

    # ✅ FORCE GUARDIAN MODE IMMEDIATELY
    st.session_state.user_state = "GUARDIAN"

    # Save to database (now Firebase!)
    try:
        success = db_handler.save_planted_trees(st.session_state.user_id, st.session_state.planted_trees)
        if success:
            # Show success feedback
            st.toast(f"✅ {plant['name']} saved!", icon="🌱")
        else:
            st.warning(f"⚠️ {plant['name']} added locally but DB save failed")
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

    return True
def standardize_plant_data(plant):
    """
    Ensure all plants have consistent field names.
    Fixes 'benefits' vs 'environmental_benefits' inconsistency.

    Args:
        plant (dict): Plant data dictionary

    Returns:
        dict: Standardized plant data
    """
    # Make a copy to avoid modifying original
    plant = plant.copy()

    # Standardize benefits fields
    if 'environmental_benefits' not in plant and 'benefits' in plant:
        plant['environmental_benefits'] = plant['benefits']
    elif 'benefits' not in plant and 'environmental_benefits' in plant:
        plant['benefits'] = plant['environmental_benefits']

    # Ensure all required fields exist with defaults
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
        if key not in plant:
            plant[key] = default_value

    return plant
# Load environment
load_dotenv()


# ===========================
# LOGIN & ONBOARDING SYSTEM
# ===========================

def show_welcome_screen():
    """Beautiful welcome/login screen - First impression!"""

    # Custom CSS for beautiful styling
    st.markdown("""
    <style>
    .welcome-container {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        margin: 20px 0;
    }
    .welcome-title {
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .welcome-subtitle {
        font-size: 20px;
        margin-bottom: 30px;
        opacity: 0.9;
    }
    .feature-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
        color: #333;
    }
    .feature-icon {
        font-size: 40px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">🌳 AirCare</div>
        <div class="welcome-subtitle">Plant Smarter. Breathe Better.</div>
        <p style="font-size: 16px; margin-top: 20px;">
            Your personal assistant for growing trees scientifically<br>
            and tracking your environmental impact in real-time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Show key features in 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🌫️</div>
            <h3>Live AQI</h3>
            <p>Monitor air quality and get personalized action plans</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3>Smart AI</h3>
            <p>Get perfect plant recommendations for your space</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Track Impact</h3>
            <p>See exactly how much CO₂ you've offset</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Login Form
    st.subheader("🚀 Get Started")

    with st.form("welcome_form"):
        st.markdown("### Create Your Profile")

        username = st.text_input(
            "Choose a username:",
            placeholder="TreeLover2025",
            help="This will be your display name in the community"
        )

        email = st.text_input(
            "Email (optional):",
            placeholder="your@email.com",
            help="For progress updates and reminders (we won't spam!)"
        )

        location_quick = st.text_input(
            "Your city:",
            placeholder="Mumbai, Delhi, Bangalore...",
            help="We'll use this to recommend the best plants for your climate"
        )

        planting_goal = st.selectbox(
            "What's your goal?",
            [
                "🌿 Improve indoor air quality",
                "🌳 Plant outdoor trees",
                "🥗 Grow herbs & vegetables",
                "📚 Learn about plants",
                "🌍 Track environmental impact"
            ]
        )

        submit = st.form_submit_button("🌱 Start My Journey", type="primary", width='stretch')

        if submit:
            errors = []

            # Validate username
            if not username or username.strip() == "":
                errors.append("⚠️ Username is required")
            elif len(username.strip()) < 3:
                errors.append("⚠️ Username must be at least 3 characters")
            elif len(username.strip()) > 20:
                errors.append("⚠️ Username must be less than 20 characters")

            # Validate location
            if not location_quick or location_quick.strip() == "":
                errors.append("⚠️ Location helps us give better recommendations")

            # Show errors or proceed
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # ... rest of logic
                # Save user data
                st.session_state.user_id = username.lower().replace(" ", "_")
                st.session_state.user_profile['username'] = username
                st.session_state.user_profile['email'] = email
                st.session_state.user_profile['goal'] = planting_goal
                st.session_state.logged_in = True

                # Try to load existing user data
                try:
                    existing_data = db_handler.load_user_data(st.session_state.user_id)
                    if existing_data:
                        st.success(f"👋 Welcome back, {username}!")
                        # Load their plants
                        saved_trees = db_handler.load_planted_trees(st.session_state.user_id)
                        if saved_trees:
                            st.session_state.planted_trees = saved_trees
                    else:
                        st.success(f"🎉 Account created! Welcome, {username}!")
                        # Save new user
                        db_handler.save_user_data(st.session_state.user_id, st.session_state.user_profile)
                except Exception as e:
                    st.warning(f"⚠️ Could not load data: {e}")
                    st.success(f"✅ Logged in as {username} (offline mode)")

                # Set initial location if provided
                if location_quick.strip():
                    try:
                        geolocator = Nominatim(user_agent="aircare_planner")
                        location = geolocator.geocode(location_quick)
                        if location:
                            st.session_state.location = {
                                "address": location.address,
                                "latitude": location.latitude,
                                "longitude": location.longitude
                            }
                            st.session_state.climate_data = get_climate_data(location.latitude, location.longitude)
                            st.session_state.soil_data = get_soil_data(location.latitude, location.longitude)
                    except Exception as e:
                        pass  # Location detection is optional
                time.sleep(1)
                st.rerun()

    # Footer
    st.markdown("---")
    st.caption(
        "🔒 Your data is stored locally and never shared. By using AirCare, you agree to plant trees responsibly.")


def detect_user_state():
    """Detect if user is Explorer or Guardian based on planted trees"""
    num_trees = len(st.session_state.get('planted_trees', []))

    if num_trees == 0:
        return "EXPLORER"
    else:
        return "GUARDIAN"


def show_first_plant_celebration():
    """Show celebration when user plants their first tree"""
    st.balloons()

    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 40px; border-radius: 20px; text-align: center; color: white;'>
        <h1 style='margin: 0; font-size: 48px;'>🎉</h1>
        <h2 style='margin: 10px 0;'>Congratulations!</h2>
        <p style='font-size: 18px; margin: 20px 0;'>
            You've just planted your first tree!<br>
            Your environmental journey begins now.
        </p>
        <p style='font-size: 14px; opacity: 0.9; margin-top: 30px;'>
            🌿 Your dashboard has transformed into Guardian Mode<br>
            Track your plant's health, log care, and watch your impact grow!
        </p>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(3)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

st.set_page_config(page_title="AirCare - Tree & Air Quality Planner", page_icon="🌳", layout="wide")


# ===========================
# USER AUTHENTICATION & PERSISTENCE
# ===========================

def init_user_session():
    """Initialize user session with persistence and Phone Number login"""
    # Auto-save to Firebase on any planted_trees change
    if 'user_id' in st.session_state and st.session_state.user_id:
        if 'planted_trees' in st.session_state and len(st.session_state.planted_trees) > 0:
            # Silent background save (don't spam the user)
            try:
                db_handler.save_planted_trees(st.session_state.user_id, st.session_state.planted_trees)
            except:
                pass  # Fail silently, don't crash the app
    # 1. If user is already logged in, ensure data is loaded and return True
    if st.session_state.get('logged_in', False) and st.session_state.get('user_id'):
        # specific check: if logged in but data is missing (e.g. after browser refresh)
        if not st.session_state.get('planted_trees'):
            try:
                user_id = st.session_state.user_id
                st.session_state.planted_trees = db_handler.load_planted_trees(user_id) or []
                st.session_state.watering_logs = db_handler.load_watering_logs(user_id) or {}
            except Exception:
                pass  # Fail silently, treat as empty garden
        return True

    # 2. If NOT logged in, decide which form to show
    st.title("🌳 Welcome to AirCare")

    # CASE A: User needs to create a profile (New User)
    if st.session_state.get('show_profile_form', False):
        st.markdown("### 🌱 Create Your Profile")
        with st.form("profile_creation_form"):
            st.markdown(f"**Phone:** {st.session_state.get('pending_phone')}")

            username = st.text_input("Choose a username:", placeholder="Green Enthusiast")
            location = st.text_input("Your city:", placeholder="Mumbai, Maharashtra")
            agree = st.checkbox("I agree to track my environmental impact 🌍")

            submit_profile = st.form_submit_button("🚀 Start My Journey", type="primary")

        if submit_profile:
            if not username or not agree:
                st.error("⚠️ Please fill all fields and agree to continue")
            else:
                user_id = f"user_{st.session_state.pending_phone}"

                # Update Session
                st.session_state.user_profile['username'] = username
                st.session_state.user_profile['location'] = location
                st.session_state.user_profile['phone'] = st.session_state.pending_phone
                st.session_state.user_id = user_id
                st.session_state.logged_in = True
                # 🔥 LOAD USER'S GARDEN FROM FIREBASE
                try:
                    loaded_trees = db_handler.load_planted_trees(st.session_state.user_id)

                    if loaded_trees and len(loaded_trees) > 0:
                        # User has plants saved in DB
                        st.session_state.planted_trees = loaded_trees
                        st.session_state.user_state = "GUARDIAN"
                        st.toast(f"✅ Welcome back! Loaded {len(loaded_trees)} plants", icon="🌿")
                    else:
                        # New user or no plants yet
                        st.session_state.planted_trees = []
                        st.session_state.user_state = "EXPLORER"
                        st.toast("🌱 Welcome! Let's plant your first tree", icon="👋")

                except Exception as e:
                    # Database error - fail gracefully
                    st.warning(f"Couldn't load your garden: {e}")
                    st.session_state.planted_trees = []
                    st.session_state.user_state = "EXPLORER"
                st.session_state.show_profile_form = False  # Reset flag

                # Save to Database
                try:
                    db_handler.save_user_data(user_id, st.session_state.user_profile)
                    st.success(f"✅ Welcome, {username}! Let's start planting! 🌱")
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving profile: {e}")

        return False  # Stop execution while on profile screen

    # CASE B: Standard Login (Phone Number Entry)
    st.markdown("### 📱 Login or Create Account")
    with st.form("phone_entry_form"):
        phone = st.text_input("Enter your phone number:", placeholder="1234567890", max_chars=10)
        submit_phone = st.form_submit_button("Continue", type="primary")

    if submit_phone:
        if not phone or len(phone) != 10 or not phone.isdigit():
            st.error("⚠️ Please enter a valid 10-digit phone number")
        else:
            user_id = f"user_{phone}"
            existing_data = db_handler.load_user_data(user_id)

            if existing_data:
                # User exists - Login immediately
                st.session_state.user_id = user_id
                st.session_state.user_profile = existing_data
                st.session_state.planted_trees = db_handler.load_planted_trees(user_id) or []
                st.session_state.watering_logs = db_handler.load_watering_logs(user_id) or {}
                st.session_state.logged_in = True

                st.success(f"✅ Welcome back, {existing_data.get('username', 'User')}!")
                time.sleep(1)
                st.rerun()
            else:
                # User is new - Trigger profile form
                st.info("📝 New user detected! Let's set up your profile.")
                st.session_state.pending_phone = phone
                st.session_state.show_profile_form = True
                st.rerun()

    return False  # Stop execution while on login screen
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


def fetch_aqi_openweather(lat, lon, api_key, max_retries=3):
    """Fetch real-time AQI data from OpenWeatherMap with retry logic"""
    if not api_key:
        return None

    for attempt in range(max_retries):
        try:
            url = "http://api.openweathermap.org/data/2.5/air_pollution"
            params = {"lat": lat, "lon": lon, "appid": api_key}
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            if 'list' in data and data['list']:
                rec = data['list'][0]
                aqi_data = {
                    "aqi_index": rec.get('main', {}).get('aqi'),
                    "components": rec.get('components', {}),
                    "dt": rec.get('dt'),
                    "timestamp": datetime.datetime.fromtimestamp(rec.get('dt', 0))
                }
                # Cache successful fetch
                st.session_state['cached_aqi'] = aqi_data
                st.session_state['cached_aqi_time'] = datetime.datetime.now()
                return aqi_data
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait 2 seconds before retry
            else:
                # Use cached data if available
                if 'cached_aqi' in st.session_state:
                    cache_age = (datetime.datetime.now() - st.session_state['cached_aqi_time']).total_seconds() / 60
                    if cache_age < 60:  # Use cache if less than 1 hour old
                        st.warning(
                            f"⚠️ Using cached AQI data ({int(cache_age)} mins old) - API temporarily unavailable")
                        return st.session_state['cached_aqi']
                st.error(f"⚠️ AQI fetch failed after {max_retries} attempts. Please try again later.")
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


    # Get full plant database
    all_trees = get_tree_data()
    all_balcony = get_balcony_plants_data()
    all_plants = all_trees + all_balcony

    # Create lookup dictionary
    plant_lookup = {plant['name']: plant for plant in all_plants}

    # Determine which plants to recommend
    if pm25 and pm25 > 50:
        plant_names = ["Areca Palm", "Boston Fern", "Rubber Plant", "Neem"]
    elif pm25 and pm25 > 25:
        plant_names = ["Snake Plant (Sansevieria)", "Spider Plant", "Peace Lily"]
    else:
        plant_names = ["Snake Plant (Sansevieria)", "Money Plant (Pothos)", "Spider Plant"]

    # Return full plant objects with reason
    recommendations = []
    for name in plant_names:
        plant = plant_lookup.get(name)
        if plant:
            plant_with_reason = plant.copy()
            # Add reason based on name
            if name == "Areca Palm":
                plant_with_reason['reason'] = "Excellent PM2.5 reducer (30% reduction)"
            elif name == "Neem":
                plant_with_reason['reason'] = "Natural air purifier (outdoor)"
            elif name == "Boston Fern":
                plant_with_reason['reason'] = "Great for particulate matter"
            elif name == "Rubber Plant":
                plant_with_reason['reason'] = "Large leaves trap dust"
            elif name == "Snake Plant (Sansevieria)":
                plant_with_reason['reason'] = "Removes formaldehyde & benzene"
            elif name == "Spider Plant":
                plant_with_reason['reason'] = "Absorbs CO and toxins"
            elif name == "Peace Lily":
                plant_with_reason['reason'] = "Filters multiple pollutants"
            elif name == "Money Plant (Pothos)":
                plant_with_reason['reason'] = "Easy care, good air cleaner"

            recommendations.append(plant_with_reason)

    return recommendations


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


def calculate_home_air_score_15q(answers):
    """
    Calculate 0-100 home air health score based on 15 questions.

    Args:
        answers (dict): Dictionary with all 15 question answers

    Returns:
        int: Score from 0-100
    """
    score = 100

    # Q1: Gas cooking (-20)
    if answers.get('gas_cooking') == "Yes":
        score -= 20

    # Q2: Smoking (-30, most critical)
    if answers.get('smoking') == "Yes":
        score -= 30

    # Q3: Carpets (-10, dust traps)
    if answers.get('carpets') == "Yes":
        score -= 10

    # Q4: Ventilation (0, -10, or -20)
    vent = answers.get('ventilation', 'Rarely')
    if vent == "Daily":
        pass  # No penalty
    elif vent == "Few times a week":
        score -= 10
    else:  # Rarely
        score -= 20

    # Q5: Plants (+2 per plant, max +10)
    plant_count = answers.get('plant_count', 0)
    score += min(10, plant_count * 2)

    # Q6: Air purifier (+10 if yes, -10 if no)
    if answers.get('purifier') == "Yes":
        score += 10
    else:
        score -= 10

    # Q7: AC filter cleaning (0, -5, -10, -15)
    ac_filter = answers.get('ac_filter', 'Never/Rarely')
    if ac_filter == "Monthly":
        pass
    elif ac_filter == "Every 3 months":
        score -= 5
    elif ac_filter == "Every 6 months":
        score -= 10
    else:  # Never/Rarely
        score -= 15

    # Q8: Incense/candles (-10)
    if answers.get('incense_candles') == "Yes":
        score -= 10

    # Q9: Pets (-5 if no purifier)
    if answers.get('pets') == "Yes":
        if answers.get('purifier') != "Yes":
            score -= 5

    # Q10: Paint age (-15 if new, -5 if medium)
    paint_age = answers.get('paint_age', '>5 years ago')
    if paint_age == "<1 year ago":
        score -= 15
    elif paint_age == "1-5 years ago":
        score -= 5

    # Q11: Traffic (-15 heavy, -8 moderate)
    traffic = answers.get('traffic', 'Light')
    if traffic == "Heavy":
        score -= 15
    elif traffic == "Moderate":
        score -= 8

    # Q12: Construction (-10)
    if answers.get('construction') == "Yes":
        score -= 10

    # Q13: Mold (-20, serious health issue)
    if answers.get('mold') == "Yes":
        score -= 20

    # Q14: Kitchen exhaust (-10 if no)
    if answers.get('kitchen_exhaust') == "No":
        score -= 10

    # Q15: Hours indoors (-5 if >12hrs)
    hours_indoors = answers.get('hours_indoors', '6-12 hours')
    if hours_indoors == ">12 hours":
        score -= 5

    # Ensure score stays within 0-100
    return max(0, min(100, score))


# ===========================
# PLANT SELECTOR MODAL (appears over any page)
# ===========================
if st.session_state.get('show_plant_selector', False):
    st.markdown("---")
    st.header("🌱 Choose Your Plant")

    # Mode selector
    mode = st.radio(
        "What are you looking for?",
        ["🔥 Quick Picks (Based on Current AQI)", "🧠 Smart Match (7-Factor Algorithm)"],
        horizontal=True
    )

    if mode == "🔥 Quick Picks (Based on Current AQI)":
        # Show AQI-based recommendations
        if st.session_state.location and OPENWEATHER_API_KEY:
            lat = st.session_state.location['latitude']
            lon = st.session_state.location['longitude']
            aqi = fetch_aqi_openweather(lat, lon, OPENWEATHER_API_KEY)

            if aqi:
                comps = aqi['components']
                plant_recs = recommend_plants_by_aqi(comps.get('pm2_5'), aqi['aqi_index'])

                st.subheader(f"🌫️ Recommended for Today's AQI ({aqi_to_label(aqi['aqi_index'])})")

                cols = st.columns(len(plant_recs))
                for idx, rec in enumerate(plant_recs):
                    with cols[idx]:
                        st.markdown(f"**{rec['name']}**")
                        st.caption(rec['reason'])

                        # FIXED: Unique key + proper add function + rerun
                        if st.button(f"Add", key=f"modal_aqi_add_{rec['name']}_{idx}"):
                            from tree_data import get_tree_data, get_balcony_plants_data

                            all_plants = get_tree_data() + get_balcony_plants_data()
                            full_plant = next((p for p in all_plants if p['name'] == rec['name']), None)

                            if full_plant:
                                # Use the safe add function (handles all state + DB)
                                if add_plant_to_garden_safe(full_plant):
                                    add_xp(50, f"Planted {rec['name']}!")
                                    check_and_award_badges()
                                    st.session_state.show_plant_selector = False
                                    st.success(f"✅ {rec['name']} added to My Garden!")
                                    time.sleep(0.5)  # Brief pause so user sees the message
                                    st.rerun()  # CRITICAL: Refresh to show Guardian mode
                            else:
                                st.error(f"❌ Plant data not found for {rec['name']}")
        else:
            st.warning("Set location first to see AQI-based recommendations")

    else:
        # Show Smart 7-Factor Recommendations
        st.subheader("🧠 Smart Recommendations (Climate + Soil + Space + Light)")

        if st.session_state.recommended_trees:
            # Show 7-factor filtered plants
            for i in range(0, min(6, len(st.session_state.recommended_trees)), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(st.session_state.recommended_trees):
                        plant = st.session_state.recommended_trees[i + j]
                        with cols[j]:
                            st.markdown(f"**{plant['name']}**")
                            st.caption(f"Match: {plant.get('suitability_score', 0)}/10")

                            if st.button(f"Select", key=f"modal_smart_{i}_{j}"):
                                st.session_state.selected_tree = plant
                                st.session_state.show_plant_selector = False
                                st.session_state.current_page = "Planting Guide"
                                st.rerun()
        else:
            st.info("Please set your location on the Home page first to see smart recommendations")

    if st.button("❌ Close", type="secondary"):
        st.session_state.show_plant_selector = False
        st.rerun()

    st.markdown("---")
# ===========================
# Initialize session state
# ===========================
def init_session_state():
    """Initialize session state with user authentication"""
    defaults = {
        # Authentication
        'logged_in': False,
        'user_id': None,
        'user_state': 'EXPLORER',  # ✅ Default to EXPLORER instead of None
        'show_celebration': False,

        # Existing fields
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
        'green_shield_data': {},

        # Beta features
        'beta_features_enabled': False  # Set to True to enable Community/Marketplace
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Auto-detect user state based on planted trees (ONLY if logged in)
    if st.session_state.get('logged_in', False):  # ✅ Safer check
        st.session_state.user_state = detect_user_state()

        # Auto-navigate to appropriate home
        if st.session_state.user_state == "GUARDIAN" and st.session_state.current_page == "Home":
            st.session_state.current_page = "🌿 My Garden"


init_session_state()
load_user_data_if_logged_in()  # <-- ADD THIS LINE
# ✅ Call only ONCE

# ===========================
# INITIALIZE USER PROFILE FIRST (Always needed)
# ===========================
if 'user_profile' not in st.session_state:
    initialize_user_profile()
    initialize_community()
    update_streak()

# ===========================
# LOGIN GATE
# ===========================
# Call the fixed function. If it returns False (not logged in), stop the app.
if not init_user_session():
    st.stop()


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
# ===========================
# STATE-AWARE SIDEBAR NAVIGATION
# ===========================

user_state = st.session_state.get('user_state', 'EXPLORER')

with st.sidebar:
    # User info at top
    st.markdown(f"### 👤 {st.session_state.user_profile.get('username', 'User')}")

    # State badge
    if user_state == "EXPLORER":
        st.markdown("🌱 **Explorer Mode**")
        st.caption("Find and plant your first tree to unlock Guardian Mode")
    else:
        st.markdown("🌿 **Guardian Mode**")
        st.caption(f"{len(st.session_state.planted_trees)} plants under care")

    st.markdown("---")
    st.markdown(f"📍 *{st.session_state.current_page}*")
    st.markdown("---")

    # CONDITIONAL NAVIGATION based on state
    if user_state == "EXPLORER":
        # Explorer navigation (pre-planting)
        page_options = [
            "Home",
            "🌫️ Air Quality Hub",
            "Planting Guide",
            "🧮 Tools",
            "About"
        ]

        for page in page_options:
            if st.button(page, key=f"nav_{page}", width='stretch'):
                navigate_to(page)

        # Show locked features
        st.markdown("---")
        st.markdown("**🔒 Locked Features:**")
        st.markdown("*Plant a tree to unlock:*")

        # Disabled buttons for locked features
        st.button("🌿 My Garden", disabled=True, width='stretch',
                  help="Plant your first tree to unlock Guardian Dashboard!")

    else:  # GUARDIAN MODE
        # Guardian navigation (post-planting)
        page_options = [
            "🌿 My Garden",  # Now contains Impact Tracker + Plant Doctor
            "🧮 Tools",
            "🌫️ Air Quality Hub",
            "About"
        ]

        for page in page_options:
            if st.button(page, key=f"nav_{page}", width='stretch'):
                navigate_to(page)

        # Special "Add Plant" button
        st.markdown("---")
        if st.button("➕ Add Another Plant", type="primary", width='stretch', key="add_plant_btn"):
            # Temporarily show Explorer tools
            st.session_state.temp_adding_plant = True
            navigate_to("🌫️ Air Quality Hub")

        # Beta features (if enabled)
        if st.session_state.beta_features_enabled:
            st.markdown("---")
            st.markdown("**🧪 Beta Features:**")
            if st.button("👥 Community",width='stretch' ):
                navigate_to("Community")
            if st.button("🛒 Marketplace", width='stretch'):
                navigate_to("Marketplace")
        # Admin panel (in sidebar)
        if "admin" in st.session_state.get('user_id', '').lower():
            st.markdown("---")
            st.subheader("👑 Admin Panel")

            if st.button("📊 View Platform Stats"):
                stats = db_handler.get_platform_stats()
                st.metric("Total Users", stats['total_users'])
                st.metric("Total Plants", stats['total_trees'])
                st.metric("Total Waterings", stats['total_waterings'])

            if st.button("📥 Download All Data"):
                all_data = db_handler.get_all_data_for_admin()
                json_str = json.dumps(all_data, indent=2)
                st.download_button(
                    label="💾 Download Database",
                    data=json_str,
                    file_name=f"aircare_full_backup_{datetime.datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
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
                        st.session_state.navigate_to = "🌫️ Air Quality Hub"
                        st.rerun()
                    else:
                        st.error("Location not found")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("Click to use device location")
            st.button("📍 Get Current Location", type="primary", disabled=True,
                      help="🚧 Under construction - Please use address search above")
            st.caption("🚧 Feature under development. Use address search for now.")

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
        st.session_state.current_page = "🌫️ Air Quality Hub"
        st.rerun()
    except Exception as e:
        st.error(f"Location error: {e}")

# ===========================
# AQI DASHBOARD (KILLER FEATURE #1)
# ===========================
# ===========================
# AIR QUALITY HUB (MERGED: AQI + RECOMMENDATIONS)
# ===========================
elif st.session_state.current_page == "🌫️ Air Quality Hub":
    st.header("🌫️ Air Quality Hub")

    if st.session_state.location is None:
        st.warning("⚠️ Set location on Home page first")
        if st.button("← Go to Home", type="primary"):
            navigate_to("Home")
    else:
        lat = st.session_state.location['latitude']
        lon = st.session_state.location['longitude']

        # ============================================
        # SECTION 1: REAL-TIME AQI DATA (TOP)
        # ============================================
        st.subheader("📍 Current Location")
        st.info(f"📍 {st.session_state.location['address']}")

        if not OPENWEATHER_API_KEY:
            st.error("🔑 Add OPENWEATHER_API_KEY to .env file")
            st.info("Get free API key at: https://openweathermap.org/api")
        else:
            # Fetch live AQI data
            with st.spinner("Fetching air quality data..."):
                aqi = fetch_aqi_openweather(lat, lon, OPENWEATHER_API_KEY)

            if aqi:
                st.session_state.last_aqi = aqi

                label = aqi_to_label(aqi['aqi_index'])
                color = aqi_to_color(aqi['aqi_index'])
                comps = aqi['components']

                # Big AQI display card
                st.markdown(f"""
                <div style='background-color: {color}; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;'>
                    <h1 style='color: white; margin: 0;'>{label}</h1>
                    <h3 style='color: white; margin: 10px 0 0 0;'>AQI Index: {aqi['aqi_index']}/5</h3>
                    <p style='color: white; margin: 5px 0 0 0;'>Updated: {aqi['timestamp'].strftime('%I:%M %p')}</p>
                </div>
                """, unsafe_allow_html=True)

                # Pollutant metrics
                st.subheader("🔬 Pollutant Levels")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("PM2.5", f"{comps.get('pm2_5', 0):.1f} µg/m³")
                col2.metric("PM10", f"{comps.get('pm10', 0):.1f} µg/m³")
                col3.metric("NO₂", f"{comps.get('no2', 0):.1f} µg/m³")
                col4.metric("O₃", f"{comps.get('o3', 0):.1f} µg/m³")

                # Action plan
                st.markdown("---")
                st.subheader("📋 YOUR ACTION PLAN FOR TODAY")
                actions = get_aqi_action_plan(aqi['aqi_index'], comps.get('pm2_5'), st.session_state.location)
                for action in actions:
                    st.markdown(f"**{action}**")
                # SECTION 2: PLANT RECOMMENDATIONS (BOTTOM)
                # ============================================
                st.markdown("---")
                st.markdown("---")
                st.header("🌱 Smart Plant Recommendations")

                if st.session_state.location is None:
                    st.warning("⚠️ Please set your location on the Home page first.")
                else:
                    # Show mode badge
                    if st.session_state.is_balcony_mode:
                        st.success("🪴 *Balcony Mode* - Space-efficient plants")
                    else:
                        st.success("🌳 *Outdoor Mode* - Ground planting trees")

                    # Display climate and soil data
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("🌡️ Climate Conditions")
                        if st.session_state.climate_data:
                            st.write(f"🌡 Avg Temperature: {st.session_state.climate_data['avg_temp']}°C")
                            st.write(f"🌧 Annual Rainfall: {st.session_state.climate_data['annual_rainfall']} mm")
                            st.write(f"💧 Humidity: {st.session_state.climate_data.get('humidity', 'N/A')}%")
                            st.write(f"🌍 Climate Zone: {st.session_state.climate_data['climate_zone']}")

                    with col2:
                        st.subheader("🪨 Soil Conditions")
                        if st.session_state.soil_data:
                            st.write(f"🪨 Soil Type: {st.session_state.soil_data['soil_type']}")
                            st.write(f"⚗ pH Level: {st.session_state.soil_data['ph_level']}")
                            st.write(f"💧 Drainage: {st.session_state.soil_data['drainage']}")
                            st.write(f"🌱 Nutrients: {st.session_state.soil_data['nutrient_level']}")

                    # Plant recommendations
                    st.subheader("🌿 Recommended Plants")

                    if st.session_state.recommended_trees:
                        # Filters
                        filter_col1, filter_col2 = st.columns(2)

                        with filter_col1:
                            purpose_filter = st.multiselect(
                                "Filter by purpose:",
                                ["Air Purification", "Shade", "Fruit Production", "Carbon Sequestration",
                                 "Biodiversity", "Edible (Herbs/Vegetables)", "Aesthetic/Decor",
                                 "Low Maintenance", "Medicinal"],
                                default=[],
                                key="purpose_filter_hub"
                            )

                        with filter_col2:
                            growth_rate_filter = st.multiselect(
                                "Filter by growth rate:",
                                ["Fast", "Medium", "Slow"],
                                default=[],
                                key="growth_filter_hub"
                            )

                        # Apply filters
                        filtered_trees = st.session_state.recommended_trees
                        if purpose_filter:
                            filtered_trees = [t for t in filtered_trees if
                                              any(p in t.get('purposes', []) for p in purpose_filter)]
                        if growth_rate_filter:
                            filtered_trees = [t for t in filtered_trees if
                                              t.get('growth_rate') in growth_rate_filter]

                        # Standardize all plant data
                        filtered_trees = [standardize_plant_data(plant) for plant in filtered_trees]

                        # Show count and "Show All" toggle
                        st.info(f"📊 Showing {len(filtered_trees)} plants matching your criteria")

                        # Toggle to show ALL plants
                        show_all = st.checkbox("🌿 Show ALL available plants (ignore filters)",
                                               key="show_all_plants_hub")
                        if show_all:
                            if st.session_state.is_balcony_mode:
                                filtered_trees = get_balcony_plants_data()
                            else:
                                filtered_trees = get_tree_data()
                            filtered_trees = [standardize_plant_data(plant) for plant in filtered_trees]
                            st.success(f"✅ Displaying all {len(filtered_trees)} available plants")

                        # Display plants in grid
                        if len(filtered_trees) == 0:
                            st.warning("No plants match your filters. Adjust criteria or enable 'Show All'.")
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

                                            if st.button(f"Select {item['name']}", key=f"select_hub_{i}_{j}"):
                                                st.session_state.selected_tree = item
                                                add_xp(5, f"Selected {item['name']}")
                                                navigate_to("Planting Guide")
                                                st.rerun()
                    else:
                        st.info("No recommendations yet. Return to Home to set location and preferences.")
                        # ============================================
                        # QUICK AQI-BASED PICKS (OPTIONAL)
                        # ============================================
                        st.markdown("---")
                        st.markdown("---")
                        st.subheader("💨 Quick AQI-Based Picks")
                        st.caption("These plants are specifically good for today's pollution levels")

                # Quick plant recommendations based on AQI
                st.markdown("---")
                st.subheader("🌱 Plants Recommended for Today's Air Quality")
                plant_recs = recommend_plants_by_aqi(comps.get('pm2_5'), aqi['aqi_index'])
                rec_cols = st.columns(len(plant_recs))
                for idx, rec in enumerate(plant_recs):
                    with rec_cols[idx]:
                        st.markdown(f"**{rec['name']}**")
                        st.caption(rec['reason'])
                        if st.button(f"Add {rec['name']}", key=f"add_plant_aqi_{idx}"):
                            # ✅ FETCH FULL PLANT DATA FROM DATABASE
                            from tree_data import get_tree_data, get_balcony_plants_data

                            # Combine all available plants
                            all_plants = get_tree_data() + get_balcony_plants_data()

                            # Find the full plant object by name
                            full_plant = next((p for p in all_plants if p['name'] == rec['name']), None)

                            if full_plant:
                                # Use the safe add function (handles all state + DB)
                                if add_plant_to_garden_safe(full_plant):
                                    add_xp(50, f"Planted {rec['name']}!")
                                    check_and_award_badges()
                                    st.success(f"✅ {rec['name']} added to My Garden!")
                                    time.sleep(0.5)  # Brief pause so user sees the message
                                    st.rerun()  # CRITICAL: Refresh to show Guardian mode
                            else:
                                st.error(f"❌ Plant data not found for {rec['name']}")
                # Health recommendations
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

                # Green shield tracker
                if st.session_state.planted_trees:
                    st.markdown("---")
                    st.subheader("🛡️ YOUR GREEN SHIELD TODAY")

                    # ✅ CALCULATE LOCALLY, DON'T SAVE TO SESSION_STATE
                    total_plants = len(st.session_state.planted_trees)
                    estimated_pm_filtered = total_plants * 2.5
                    estimated_voc_filtered = total_plants * 15

                    shield_col1, shield_col2, shield_col3 = st.columns(3)
                    shield_col1.metric("🌿 Active Plants", total_plants)
                    shield_col2.metric("💨 Est. PM2.5 Filtered", f"{estimated_pm_filtered:.1f}g today")
                    shield_col3.metric("🧪 Est. VOCs Removed", f"{estimated_voc_filtered:.0f}µg today")

                    st.info("💡 Your plants are actively cleaning your air!")
            else:
                st.error("Unable to fetch AQI data. Check your API key or try again later.")

        # ============================================

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

        if st.button("✅ Add to My Garden", type="primary", key="add_from_planting_guide"):
            tree_to_track = tree.copy()
            tree_to_track['id'] = str(uuid.uuid4())  # UNIQUE ID
            tree_to_track['planted_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            tree_to_track['status'] = "Newly Planted"
            tree_to_track['health'] = "Good"

            st.session_state.planted_trees.append(tree_to_track)
            st.session_state.user_profile['trees_planted'] = len(st.session_state.planted_trees)

            add_xp(50, f"Planted {tree['name']}!")
            check_and_award_badges()

            st.success(f"✅ {tree['name']} added! View in → 🌿 My Garden.")

            # AUTO-NAVIGATE
            # Track This Plant

# ===========================

# (MERGED FROM TPP.py for more detail)
# ===========================
# ===========================
# MY GARDEN PAGE (Now uses Guardian Dashboard)
# ===========================
elif st.session_state.current_page == "🌿 My Garden":

    if st.session_state.user_state == "EXPLORER":
        # Empty State for Explorer mode
        st.markdown("""
        <div style='text-align: center; padding: 80px 20px;'>
            <h1 style='font-size: 64px; margin: 0;'>🌱</h1>
            <h2 style='color: #666; margin: 20px 0;'>Your Garden Awaits</h2>
            <p style='font-size: 18px; color: #888; max-width: 500px; margin: 0 auto 40px;'>
                Plant your first tree to unlock your personal garden dashboard
                and start tracking your environmental impact!
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Show what they'll unlock
        st.markdown("### 🔓 What You'll Unlock:")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("""
            **📊 Impact Tracker**
            - Live CO₂ offset
            - Oxygen production
            - Pollutant removal
            """)

        with col2:
            st.info("""
            **🩺 Plant Doctor**
            - Photo-based diagnosis
            - Health recommendations
            - Care reminders
            """)

        with col3:
            st.info("""
            **🏆 Achievements**
            - Badges & milestones
            - Streak tracking
            - Community recognition
            """)

        st.markdown("---")

        # CTA Button
        col_spacer, col_btn, col_spacer2 = st.columns([1, 2, 1])
        with col_btn:
            if st.button("🌱 Find Your Perfect Plant", type="primary", width='stretch', key="empty_state_cta"):
                navigate_to("🌫️ Air Quality Hub")

    else:
        # GUARDIAN MODE - Show the super dashboard!
        if st.session_state.get('show_celebration', False):
            show_first_plant_celebration()
            st.session_state.show_celebration = False
            time.sleep(2)
            st.rerun()
        else:
            show_guardian_super_dashboard()

# ===========================

# ===========================
# ===========================
# TOOLS PAGE (3 TABS: AIR CALCULATOR, HOME AIR SCORE, PLANT DOCTOR)
# ===========================
elif st.session_state.current_page == "🧮 Tools":
    st.header("🧮 AirCare Tools")
    st.info(
        "💡 Use these tools to calculate plant needs, assess your home's air quality, and diagnose plant health issues")

    # Create 3 tabs
    tab1, tab2, tab3 = st.tabs(["🧮 Air Calculator", "🏠 Home Air Score", "🩺 Plant Doctor"])

    # ============================================
    # TAB 1: AIR CALCULATOR
    # ============================================
    with tab1:
        st.subheader("🧮 Indoor Air Purifier Calculator")
        st.markdown("Calculate how many plants you need to purify your indoor space")

        room_sqft = st.number_input("Room area (square feet):", min_value=10, max_value=2000, value=150, step=10,
                                    key="calc_room_sqft")
        plant_choice = st.selectbox("Choose plant type:", list(PLANT_AIR_DATA.keys()), key="calc_plant_choice")

        if st.button("🧮 Calculate", type="primary", key="calc_button"):
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
        st.dataframe(df, width='stretch', hide_index=True)

    # ============================================
    # TAB 2: HOME AIR SCORE
    # ============================================
    with tab2:
        st.subheader("🏠 Home Air Health Score (15-Point Assessment)")
        st.info("📋 Complete all 15 questions for accurate air quality assessment")

        with st.form("home_air_form_tools"):
            st.markdown("### 🏠 Indoor Environment")
            q1 = st.radio("1. Do you cook with gas stove indoors?", ["Yes", "No"], index=1, key="q1_tools")
            q2 = st.radio("2. Does anyone smoke indoors?", ["Yes", "No"], index=1, key="q2_tools")
            q3 = st.radio("3. Do you have carpets or rugs?", ["Yes", "No"], index=0, key="q3_tools")

            st.markdown("### 💨 Ventilation & Air Quality")
            q4 = st.radio("4. How often do you ventilate your home?",
                          ["Daily", "Few times a week", "Rarely"], index=0, key="q4_tools")
            q6 = st.radio("5. Do you use an air purifier?", ["Yes", "No"], index=1, key="q6_tools")
            q7 = st.radio("6. How often do you clean AC filters?",
                          ["Monthly", "Every 3 months", "Every 6 months", "Never/Rarely"], index=1, key="q7_tools")
            q14 = st.radio("7. Do you have a kitchen exhaust fan?", ["Yes", "No"], index=0, key="q14_tools")

            st.markdown("### 🌿 Plants & Indoor Air")
            q5 = st.number_input("8. Number of air-purifying plants in your home?",
                                 min_value=0, max_value=100, value=2, key="q5_tools")

            st.markdown("### 🗒️ Home Conditions")
            q8 = st.radio("9. Do you burn incense or candles daily?", ["Yes", "No"], index=1, key="q8_tools")
            q9 = st.radio("10. Do you have pets indoors?", ["Yes", "No"], index=0, key="q9_tools")
            q10 = st.radio("11. When was your home last painted?",
                           ["<1 year ago", "1-5 years ago", ">5 years ago"], index=2, key="q10_tools")
            q13 = st.radio("12. Do you have visible mold or dampness?", ["Yes", "No"], index=1, key="q13_tools")

            st.markdown("### 🌆 External Factors")
            q11 = st.radio("13. How heavy is traffic near your home?",
                           ["Heavy", "Moderate", "Light"], index=2, key="q11_tools")
            q12 = st.radio("14. Is there active construction nearby?", ["Yes", "No"], index=1, key="q12_tools")

            st.markdown("### ⏰ Lifestyle")
            q15 = st.radio("15. Hours spent indoors daily?",
                           ["<6 hours", "6-12 hours", ">12 hours"], index=1, key="q15_tools")

            submitted = st.form_submit_button("🧮 Calculate My Air Score", type="primary")

        # IMPORTANT: Process form submission OUTSIDE the form block
        if submitted:
            answers = {
                'gas_cooking': q1,
                'smoking': q2,
                'carpets': q3,
                'ventilation': q4,
                'plant_count': q5,
                'purifier': q6,
                'ac_filter': q7,
                'incense_candles': q8,
                'pets': q9,
                'paint_age': q10,
                'traffic': q11,
                'construction': q12,
                'mold': q13,
                'kitchen_exhaust': q14,
                'hours_indoors': q15
            }

            # Calculate score using 15-question function
            score = calculate_home_air_score_15q(answers)

            # Determine color and grade
            if score >= 80:
                color, grade = "green", "Excellent 🌟"
            elif score >= 60:
                color, grade = "lightgreen", "Good ✅"
            elif score >= 40:
                color, grade = "orange", "Fair ⚠️"
            else:
                color, grade = "red", "Poor ❌"

            # Display score
            st.markdown(f"""
            <div style='background-color: {color}; padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0;'>
                <h1 style='color: white; margin: 0;'>{score}/100</h1>
                <h2 style='color: white; margin: 10px 0 0 0;'>{grade}</h2>
            </div>
            """, unsafe_allow_html=True)

            # Recommendations
            st.subheader("📋 Recommendations")

            if answers['gas_cooking'] == "Yes":
                st.markdown("**✅ Install kitchen exhaust fan**")
            if answers['smoking'] == "Yes":
                st.markdown("**⚠️ CRITICAL: Stop smoking indoors immediately**")
            if answers['ventilation'] == "Rarely":
                st.markdown("**✅ Open windows 15-30 minutes daily**")
            if answers['plant_count'] < 5:
                st.markdown(f"**✅ Add {5 - answers['plant_count']} more air-purifying plants**")
            if answers['purifier'] == "No" and score < 60:
                st.markdown("**✅ Consider investing in a HEPA air purifier**")
            if answers['mold'] == "Yes":
                st.markdown("**⚠️ URGENT: Address mold/dampness issues - health hazard**")
            if answers['paint_age'] == "<1 year ago":
                st.markdown("**⚠️ Fresh paint releases VOCs - ventilate frequently**")
            if answers['traffic'] == "Heavy":
                st.markdown("**✅ Keep windows closed during peak traffic hours**")

            # Overall feedback
            if score >= 80:
                st.success("🎉 Excellent! Your home has great air quality. Keep it up!")
            elif score >= 60:
                st.info("👍 Good work! A few improvements will make it even better.")
            elif score >= 40:
                st.warning("⚠️ Your indoor air quality needs attention. Follow the recommendations above.")
            else:
                st.error("❌ Critical: Your indoor air quality is poor. Please take immediate action!")

    # ============================================
    # TAB 3: PLANT DOCTOR
    # ============================================
    with tab3:
        st.subheader("🩺 AI Plant Doctor")
        st.markdown("Upload a photo of your plant and get instant health diagnosis")

        uploaded = st.file_uploader("📸 Upload plant photo", type=['jpg', 'jpeg', 'png'], key="plant_doctor_upload")

        if uploaded:
            bytes_data = uploaded.getvalue()
            st.image(bytes_data, use_column_width=True)

            if st.button("🔬 Analyze Plant Health", type="primary", key="analyze_plant_button"):
                with st.spinner("Analyzing plant health..."):
                    analysis = analyze_plant_image(bytes_data)
                    issues, recommendations = diagnose_plant_health(analysis)

                st.subheader("🔍 Analysis Results")

                if 'error' not in analysis:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🟢 Green Coverage", f"{analysis['green_ratio'] * 100:.1f}%")
                    col2.metric("🟤 Brown/Dead", f"{analysis['brown_ratio'] * 100:.1f}%")
                    col3.metric("💨 Dust Level", "High" if analysis['dusty'] else "Normal")

                st.subheader("⚠️ Detected Issues")
                for issue in issues:
                    st.markdown(f"- {issue}")

                st.subheader("💡 Care Recommendations")
                for rec in recommendations:
                    st.markdown(f"- {rec}")

                # Additional tips
                st.markdown("---")
                st.info("""
                **💡 General Plant Care Tips:**
                - Water when top 2cm of soil is dry
                - Clean leaves weekly with damp cloth
                - Rotate plant weekly for even growth
                - Check for pests during watering
                - Fertilize every 2-4 weeks during growing season
                """)

# ===========================
# Impact Tracker
# (MERGED FROM TPP.py for more detail)
# ===========================
elif st.session_state.current_page == "Impact Tracker":
    st.info("📊 Impact tracking is now part of your Garden Dashboard!")
    st.markdown("All your environmental impact metrics are integrated into **🌿 My Garden**.")
    if st.button("🌿 Go to My Garden", type="primary", key="impact_to_garden"):
        navigate_to("🌿 My Garden")
    st.stop()
elif st.session_state.current_page == "🩺 Plant Doctor":
    st.info("🩺 Plant Doctor is now integrated into your Garden Dashboard!")
    st.markdown("Upload plant photos directly from each plant card in **🌿 My Garden**.")
    if st.button("🌿 Go to My Garden", type="primary", key="doctor_to_garden"):
        navigate_to("🌿 My Garden")
    st.stop()
# ===========================
# MARKETPLACE
# ===========================
elif st.session_state.current_page == "🛒 Marketplace":
    st.header("🛒 AirCare Marketplace")
    st.info("🚧 **Coming Soon!** Browse plants, seeds, pots, and air quality products")

    # Import marketplace data
    try:
        from marketplace_data import get_marketplace_products

        products = get_marketplace_products()
    except ImportError:
        get_marketplace_products = None
        st.error("⚠️ marketplace_data.py not found. Please create the file.")
        products = []

    if products:
        # Category filter
        all_categories = list(set([p['category'] for p in products]))
        selected_category = st.selectbox(
            "Filter by category:",
            ["All Categories"] + sorted(all_categories),
            key="marketplace_category_filter"
        )

        # Filter products
        if selected_category != "All Categories":
            filtered_products = [p for p in products if p['category'] == selected_category]
        else:
            filtered_products = products

        st.markdown(f"### 🛍️ Showing {len(filtered_products)} products")

        # Display products in 3-column grid
        for i in range(0, len(filtered_products), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(filtered_products):
                    product = filtered_products[i + j]
                    with cols[j]:
                        # Product card
                        st.markdown(f"### {product['name']}")
                        st.markdown(f"**Category:** {product['category']}")
                        st.markdown(f"**Price:** ₹{product['price']}")
                        st.caption(product['description'])

                        if 'benefits' in product and product['benefits']:
                            st.markdown(f"*Benefits:* {product['benefits']}")

                        # Disabled "Add to Cart" button with coming soon message
                        st.button(
                            "🛒 Add to Cart",
                            key=f"cart_{product['name']}_{i}_{j}",
                            disabled=True,
                            help="Coming soon! Marketplace under development"
                        )
                        st.caption("🚧 Coming soon")

                        st.markdown("---")
    else:
        st.warning("No products available. Check marketplace_data.py file.")
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
        if st.button("🌳 Start Outdoor Planting", type="primary", width='stretch'):
            st.session_state.is_balcony_mode = False
            navigate_to("Home")

    with col2:
        if st.button("🪴 Start Balcony Garden", type="primary", width='stretch'):
            st.session_state.is_balcony_mode = True
            navigate_to("Home")

    with col3:
        if st.button("👥 Join Community", type="secondary", width='stretch'):
            navigate_to("Community")


st.markdown("---")

