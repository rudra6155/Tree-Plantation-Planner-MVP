"""
Guardian Super Dashboard - The Ultimate Plant Care Hub
✅ UPDATED WITH FIX #3: Plant removal functionality
"""

import streamlit as st
import datetime
import plotly.graph_objects as go
from impact_calculator import calculate_impact
import numpy as np
from PIL import Image
import io
import db_handler


# ===========================
# PLANT DOCTOR FUNCTIONS
# ===========================

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


def calculate_days_since_planted(planted_date_str):
    """Calculate days since a plant was planted"""
    try:
        planted = datetime.datetime.strptime(planted_date_str, "%Y-%m-%d")
        today = datetime.datetime.now()
        delta = today - planted
        return delta.days
    except Exception as e:
        return 0


def get_health_emoji(health_status):
    """Return emoji for health status"""
    health_emojis = {
        "Excellent": "✅",
        "Good": "👍",
        "Fair": "⚠️",
        "Needs Attention": "🔴",
        "Poor": "💀"
    }
    return health_emojis.get(health_status, "❓")


def get_status_progress(status):
    """Get progress percentage for growth status"""
    progress_map = {
        "Newly Planted": 0.15,
        "Seedling": 0.35,
        "Sapling": 0.60,
        "Young Tree": 0.85,
        "Mature Tree": 1.0
    }
    return progress_map.get(status, 0.15)


def suggest_next_action(plant):
    """AI-powered suggestion for next care action"""
    plant_id = plant['id']

    # Check watering logs
    logs = st.session_state.watering_logs.get(plant_id, [])

    if not logs:
        return "💧 Water your plant for the first time!"

    # Get last watering
    last_watered = logs[-1]

    # Handle different storage formats
    if isinstance(last_watered, dict):
        return "💧 Water your plant regularly"
    elif isinstance(last_watered, str):
        try:
            last_watered = datetime.datetime.fromisoformat(last_watered)
            days_since = (datetime.datetime.now() - last_watered).days
        except:
            return "💧 Water your plant regularly"
    else:
        # It's a datetime object
        try:
            days_since = (datetime.datetime.now() - last_watered).days
        except:
            return "💧 Water your plant regularly"

    # Different plants have different needs
    plant_name = plant.get('name', '')

    # Balcony plants (need frequent watering)
    if any(x in plant_name for x in ['Snake Plant', 'Tulsi', 'Mint', 'Aloe', 'Spider', 'Money', 'Jade', 'Peace Lily']):
        if days_since >= 3:
            return f"💧 Water needed! Last watered {days_since} days ago"
        elif days_since >= 14:
            return "🌱 Time to add fertilizer"
        else:
            return "✅ All good! Check again tomorrow"

    # Outdoor trees (less frequent)
    else:
        if days_since >= 7:
            return f"💧 Water needed! Last watered {days_since} days ago"
        elif days_since >= 21:
            return "🌱 Consider adding organic fertilizer"
        else:
            return "✅ Doing great! Water in a few days"


def show_guardian_super_dashboard():
    """
    THE ULTIMATE DASHBOARD
    ✅ NOW WITH PLANT REMOVAL FEATURE

    Everything a plant guardian needs in one scrollable page:
    - Live impact metrics (top)
    - Plant cards with integrated actions
    - Inline Plant Doctor
    - ✅ NEW: Remove plant button
    - Detailed impact projections (bottom)
    """

    st.title("🌿 Your Garden Dashboard")
    st.caption("Guardian Mode • Caring for your plants with science")

    # ============================================
    # SECTION 1: LIVE IMPACT METRICS (Always Visible)
    # ============================================

    st.markdown("### 📊 Real-Time Environmental Impact")

    impact = calculate_impact(st.session_state.planted_trees)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🌳 Plants",
            value=len(st.session_state.planted_trees),
            delta=f"{len([p for p in st.session_state.planted_trees if p.get('status') != 'Newly Planted'])} growing"
        )

    with col2:
        st.metric(
            label="🌍 CO₂ Offset (kg/year)",
            value=f"{impact['carbon_sequestered']:.1f}",
            delta="Equivalent to planting trees!"
        )

    with col3:
        st.metric(
            label="💨 O₂ Produced (kg/year)",
            value=f"{impact['oxygen_produced']:.1f}",
            delta="Breathing easier"
        )

    with col4:
        st.metric(
            label="🫁 Pollutants Removed (kg/year)",
            value=f"{impact['pollutants_removed']:.1f}",
            delta="Cleaner air"
        )

    st.markdown("---")

    # ============================================
    # SECTION 2: MY PLANTS (Cards with Actions)
    # ============================================

    st.markdown("### 🌱 My Plants")

    if not st.session_state.planted_trees:
        st.info("No plants yet! Add your first plant below.")
    else:
        # Display each plant as a card
        for idx, plant in enumerate(st.session_state.planted_trees):
            plant_id = plant.get('id', f'plant_{idx}')
            name = plant.get('name', 'Unknown Plant')
            status = plant.get('status', 'Newly Planted')
            health = plant.get('health', 'Good')
            planted_date = plant.get('planted_date', datetime.datetime.now().strftime("%Y-%m-%d"))

            days_old = calculate_days_since_planted(planted_date)
            progress = get_status_progress(status)
            next_action = suggest_next_action(plant)
            health_emoji = get_health_emoji(health)

            # Plant card container
            with st.container():
                st.markdown(f"#### {name}")

                # Top row: Age + Health
                col_age, col_health = st.columns(2)

                with col_age:
                    st.metric("🗓 Plant Age", f"{days_old} days")

                with col_health:
                    st.markdown(f"**Health:** {health_emoji}")
                    st.caption(health)

                # Info row: Status + Progress
                col_info1, col_info2 = st.columns(2)

                with col_info1:
                    st.markdown(f"**Growth Stage:** {status}")
                    st.progress(progress)
                    st.caption(f"🌱 {int(progress * 100)}% to maturity")

                with col_info2:
                    st.markdown(f"**Next Task:**")
                    st.info(next_action)

                # Action row: Buttons + Plant Doctor
                col_actions, col_doctor = st.columns([1, 2])

                with col_actions:
                    st.markdown("**Quick Actions:**")

                    # Watering button
                    if st.button("💧 Log Water", key=f"water_{plant_id}"):
                        # Initialize log if doesn't exist
                        if plant_id not in st.session_state.watering_logs:
                            st.session_state.watering_logs[plant_id] = []

                        st.session_state.watering_logs[plant_id].append(datetime.datetime.now().isoformat())

                        # Save to database
                        if st.session_state.get('user_id'):
                            try:
                                db_handler.save_watering_log(st.session_state.user_id, plant_id)
                            except:
                                pass

                        st.success("✅ Watered! +10 XP")
                        st.rerun()

                    # Watering stats
                    water_count = len(st.session_state.watering_logs.get(plant_id, []))
                    st.caption(f"✅ Watered {water_count} times total")

                    # ✅ FIX #3: REMOVE PLANT BUTTON
                    with st.expander("⚙️ More Options"):
                        st.markdown("**Update Status:**")

                        new_status = st.selectbox(
                            "Growth Stage:",
                            ["Newly Planted", "Seedling", "Sapling", "Young Tree", "Mature Tree"],
                            index=["Newly Planted", "Seedling", "Sapling", "Young Tree", "Mature Tree"].index(status),
                            key=f"status_update_{plant_id}"
                        )

                        new_health = st.selectbox(
                            "Health:",
                            ["Excellent", "Good", "Fair", "Needs Attention", "Poor"],
                            index=["Excellent", "Good", "Fair", "Needs Attention", "Poor"].index(health),
                            key=f"health_update_{plant_id}"
                        )

                        col_save, col_remove = st.columns(2)

                        with col_save:
                            if st.button("💾 Save", key=f"save_{plant_id}", use_container_width=True):
                                plant['status'] = new_status
                                plant['health'] = new_health

                                # Save to database
                                if st.session_state.get('user_id'):
                                    try:
                                        db_handler.save_planted_trees(st.session_state.user_id,
                                                                      st.session_state.planted_trees)
                                    except:
                                        pass

                                st.success("Updated! +20 XP")
                                st.rerun()

                        with col_remove:
                            # ✅ NEW: REMOVE BUTTON
                            if st.button("🗑️ Remove", key=f"remove_{plant_id}", type="secondary",
                                         use_container_width=True):
                                st.session_state[f'confirm_remove_{plant_id}'] = True
                                st.rerun()

                        # ✅ CONFIRMATION DIALOG
                        if st.session_state.get(f'confirm_remove_{plant_id}', False):
                            st.warning(f"⚠️ Are you sure you want to remove **{name}** from your garden?")

                            col_yes, col_no = st.columns(2)

                            with col_yes:
                                if st.button("Yes, remove it", key=f"confirm_yes_{plant_id}", type="primary"):
                                    # Remove from session state
                                    st.session_state.planted_trees = [
                                        p for p in st.session_state.planted_trees if p['id'] != plant_id
                                    ]

                                    # Remove watering logs
                                    if plant_id in st.session_state.watering_logs:
                                        del st.session_state.watering_logs[plant_id]

                                    # Update user state if no plants left
                                    if len(st.session_state.planted_trees) == 0:
                                        st.session_state.user_state = "EXPLORER"

                                    # Save to database
                                    try:
                                        db_handler.save_planted_trees(st.session_state.user_id,
                                                                      st.session_state.planted_trees)
                                    except:
                                        pass

                                    st.success(f"🗑️ {name} removed from garden")
                                    del st.session_state[f'confirm_remove_{plant_id}']
                                    st.rerun()

                            with col_no:
                                if st.button("No, keep it", key=f"confirm_no_{plant_id}"):
                                    del st.session_state[f'confirm_remove_{plant_id}']
                                    st.rerun()

                with col_doctor:
                    st.markdown("**🩺 AI Plant Doctor:**")

                    photo = st.file_uploader(
                        "Upload photo for health check",
                        type=['jpg', 'png', 'jpeg'],
                        key=f"scan_{plant_id}",
                        help="Take a clear photo of your plant's leaves"
                    )

                    if photo:
                        with st.spinner("🔬 Analyzing plant health..."):
                            img_bytes = photo.getvalue()
                            st.image(img_bytes, width=200, caption="Analyzing this photo")

                            # Use local functions
                            analysis = analyze_plant_image(img_bytes)
                            issues, recommendations = diagnose_plant_health(analysis)

                        st.success("✅ Analysis Complete!")

                        with st.expander("📋 Full Health Report", expanded=True):
                            st.markdown("**🔍 Issues Detected:**")
                            for issue in issues:
                                st.markdown(f"- {issue}")

                            st.markdown("**💡 Recommendations:**")
                            for rec in recommendations[:5]:  # Limit to top 5
                                st.markdown(f"- {rec}")

                st.markdown("---")

    # ============================================
    # SECTION 3: ADD ANOTHER PLANT
    # ============================================

    col_spacer1, col_button, col_spacer2 = st.columns([1, 2, 1])

    with col_button:
        if st.button("➕ Add Another Plant", type="primary"):
            # Navigate back to Home to select plant
            st.session_state.page = "Home"
            st.rerun()

    st.markdown("---")

    # ============================================
    # SECTION 4: DETAILED IMPACT CHARTS
    # ============================================

    st.markdown("### 📈 Projected Impact Over Time")

    # 10-year projection
    years = list(range(1, 11))
    carbon_seq = [impact['carbon_sequestered'] * (year ** 0.8) for year in years]
    oxygen_prod = [impact['oxygen_produced'] * (year ** 0.7) for year in years]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=years,
        y=carbon_seq,
        mode='lines+markers',
        name='Carbon Offset (kg)',
        line=dict(color='#2E7D32', width=3),
        marker=dict(size=8)
    ))

    fig.add_trace(go.Scatter(
        x=years,
        y=oxygen_prod,
        mode='lines+markers',
        name='Oxygen Produced (kg)',
        line=dict(color='#1976D2', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title='Your Environmental Benefits Over the Next Decade',
        xaxis_title='Years from Now',
        yaxis_title='Amount (kg)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # ============================================
    # SECTION 5: FUN FACTS & COMPARISONS
    # ============================================

    st.markdown("### 💡 What Your Impact Means")

    fun_col1, fun_col2 = st.columns(2)

    with fun_col1:
        st.info(f"""
        **Your CO₂ offset is equivalent to:**
        - 🚗 **{impact['carbon_sequestered'] * 5:.0f} km** of car driving avoided
        - 📱 **{impact['carbon_sequestered'] * 200:.0f}** smartphone charges
        - 🏠 **{impact['carbon_sequestered'] / 0.5:.1f} days** of home electricity
        - ✈️ **{impact['carbon_sequestered'] / 90:.2f}** short flights prevented
        """)

    with fun_col2:
        st.success(f"""
        **Your oxygen production equals:**
        - 🫁 **{impact['oxygen_produced'] / 0.8:.0f} person-days** of breathing
        - 🌳 Impact of **{len(st.session_state.planted_trees) * 10:.0f} more trees** (when mature)
        - 💚 Enough for **{impact['oxygen_produced'] / 365:.1f} people** for a full day
        - 🌍 Making the world greener, one plant at a time!
        """)

    # ============================================
    # SECTION 6: FOOTER WITH MOTIVATION
    # ============================================

    st.markdown("---")

    st.markdown("""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; color: white; margin: 20px 0;'>
        <h3 style='margin: 0;'>🌟 Keep Growing!</h3>
        <p style='margin: 10px 0 0 0; opacity: 0.9;'>
            Every drop of water, every day of care, makes a difference.<br>
            You're not just growing plants — you're growing hope for our planet.
        </p>
    </div>
    """, unsafe_allow_html=True)