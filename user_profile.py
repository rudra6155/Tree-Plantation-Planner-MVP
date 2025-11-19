"""
User Profile and Gamification System
"""
import streamlit as st
from datetime import datetime


def initialize_user_profile():
    """Initialize user profile in session state"""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'username': 'Green Enthusiast',
            'level': 1,
            'xp': 0,
            'green_score': 0,
            'trees_planted': 0,
            'join_date': datetime.now().strftime("%Y-%m-%d"),
            'streak_days': 0,
            'last_active_date': datetime.now().strftime("%Y-%m-%d"),
            'badges': [],
            'total_co2_offset': 0.0,
            'profile_complete': False
        }


def add_xp(amount, reason=""):
    """Add XP and level up if needed"""
    st.session_state.user_profile['xp'] += amount

    # Level up logic (500 XP per level)
    xp_for_next_level = st.session_state.user_profile['level'] * 500
    if st.session_state.user_profile['xp'] >= xp_for_next_level:
        st.session_state.user_profile['level'] += 1
        st.balloons()
        st.success(f"🎉 Level Up! You're now Level {st.session_state.user_profile['level']}")

    if reason:
        st.toast(f"+{amount} XP: {reason}", icon="⭐")


def award_badge(badge_name, badge_icon, badge_description):
    """Award a badge to user"""
    # Check if badge already exists
    existing_badges = [b['name'] for b in st.session_state.user_profile['badges']]

    if badge_name not in existing_badges:
        st.session_state.user_profile['badges'].append({
            'name': badge_name,
            'icon': badge_icon,
            'description': badge_description,
            'earned_date': datetime.now().strftime("%Y-%m-%d")
        })
        st.success(f"🏆 New Badge Earned: {badge_icon} {badge_name}")
        st.balloons()
        add_xp(50, f"Earned {badge_name} badge!")


def calculate_green_score():
    """Calculate total green score from planted trees"""
    total_score = 0

    for tree in st.session_state.get('planted_trees', []):
        # Base score
        score = 10

        # Health bonus
        health_bonus = {
            'Excellent': 5,
            'Good': 3,
            'Fair': 1,
            'Needs Attention': 0,
            'Poor': -2
        }
        score += health_bonus.get(tree.get('health', 'Good'), 0)

        # Maturity bonus
        status_bonus = {
            'Newly Planted': 0,
            'Seedling': 2,
            'Sapling': 5,
            'Young Tree': 10,
            'Mature Tree': 20
        }
        score += status_bonus.get(tree.get('status', 'Newly Planted'), 0)

        # Longevity bonus (planted > 30 days)
        try:
            planted_date = datetime.strptime(tree.get('planted_date', datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
            days_planted = (datetime.now() - planted_date).days
            if days_planted > 30:
                score += 10
            if days_planted > 90:
                score += 20
        except:
            pass

        total_score += score

    st.session_state.user_profile['green_score'] = total_score
    return total_score


def get_rank_title(level):
    """Get rank title based on level"""
    ranks = {
        1: "🌱 Seedling",
        2: "🌿 Sprout",
        3: "🪴 Gardener",
        5: "🌳 Tree Guardian",
        7: "🌲 Forest Keeper",
        10: "🏞️ Eco Warrior",
        15: "🌍 Planet Protector"
    }

    for min_level in sorted(ranks.keys(), reverse=True):
        if level >= min_level:
            return ranks[min_level]
    return "🌱 Seedling"


def update_streak():
    """Update daily streak"""
    today = datetime.now().date()
    last_active = st.session_state.user_profile.get('last_active_date')

    if last_active:
        try:
            last_date = datetime.strptime(last_active, "%Y-%m-%d").date()
            days_diff = (today - last_date).days

            if days_diff == 0:
                # Same day, do nothing
                pass
            elif days_diff == 1:
                # Consecutive day
                st.session_state.user_profile['streak_days'] += 1

                # Milestone bonuses
                if st.session_state.user_profile['streak_days'] in [7, 30, 100]:
                    bonus = st.session_state.user_profile['streak_days'] * 10
                    add_xp(bonus, f"{st.session_state.user_profile['streak_days']}-day streak!")

                    if st.session_state.user_profile['streak_days'] == 7:
                        award_badge("Week Warrior", "🔥", "Logged in for 7 consecutive days")
            else:
                # Streak broken
                st.session_state.user_profile['streak_days'] = 1
        except:
            st.session_state.user_profile['streak_days'] = 1
    else:
        st.session_state.user_profile['streak_days'] = 1

    st.session_state.user_profile['last_active_date'] = today.strftime("%Y-%m-%d")


def check_and_award_badges():
    """Check conditions and award badges automatically"""
    planted_count = len(st.session_state.get('planted_trees', []))

    # First Sprout - Plant first tree
    if planted_count >= 1:
        award_badge("First Sprout", "🌱", "Planted your first tree!")

    # Tree Hugger - Track 10 trees
    if planted_count >= 10:
        award_badge("Tree Hugger", "🌳", "Tracked 10 trees!")

    # Green Thumb - 5 plants with Excellent health
    excellent_plants = [p for p in st.session_state.get('planted_trees', [])
                        if p.get('health') == 'Excellent']
    if len(excellent_plants) >= 5:
        award_badge("Green Thumb", "💚", "5 plants in excellent health!")

    # Balcony Boss - 5+ balcony plants
    balcony_plants = [p for p in st.session_state.get('planted_trees', [])
                      if 'space_required' in p]
    if len(balcony_plants) >= 5:
        award_badge("Balcony Boss", "🏙️", "Created a balcony garden!")

    # Carbon Hero - Offset 100kg CO2
    if st.session_state.user_profile.get('total_co2_offset', 0) >= 100:
        award_badge("Carbon Hero", "🌍", "Offset 100 kg of CO₂!")

    # Rising Star - Reach Level 3
    if st.session_state.user_profile['level'] >= 3:
        award_badge("Rising Star", "⭐", "Reached Level 3!")


def display_profile_sidebar():
    """Display user profile in sidebar"""
    with st.sidebar:
        st.markdown("### 👤 Your Profile")

        user = st.session_state.user_profile

        # Username with edit option
        if st.button("✏️ Edit Name", key="edit_name_btn"):
            st.session_state.editing_name = True

        if st.session_state.get('editing_name', False):
            new_name = st.text_input("Username:", value=user['username'], key="username_input")
            if st.button("Save", key="save_name_btn"):
                st.session_state.user_profile['username'] = new_name
                st.session_state.editing_name = False
                if not user['profile_complete']:
                    st.session_state.user_profile['profile_complete'] = True
                    add_xp(25, "Completed profile!")
                st.rerun()
        else:
            st.markdown(f"**{user['username']}**")

        # Level and Rank
        st.markdown(f"**{get_rank_title(user['level'])}**")

        # Stats in columns
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", user['level'])
            st.metric("Trees", user['trees_planted'])
        with col2:
            st.metric("XP", user['xp'])
            green_score = calculate_green_score()
            st.metric("Green Score", green_score)

        # Progress bar to next level
        xp_for_next = user['level'] * 500
        progress = min(user['xp'] / xp_for_next if xp_for_next > 0 else 1.0, 1.0)
        st.progress(progress)
        st.caption(f"{user['xp']} / {xp_for_next} XP to Level {user['level'] + 1}")

        # Streak
        if user['streak_days'] > 0:
            st.markdown(f"🔥 **{user['streak_days']}-day streak**")

        # Badges
        if user['badges']:
            with st.expander(f"🏆 Badges ({len(user['badges'])})"):
                for badge in user['badges']:
                    st.write(f"{badge['icon']} **{badge['name']}**")
                    st.caption(badge['description'])
        else:
            st.caption("🏆 No badges yet - start planting!")

        st.markdown("---")