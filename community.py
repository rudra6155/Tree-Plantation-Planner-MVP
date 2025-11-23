"""
Community Feed System
"""
import streamlit as st
from datetime import datetime
import uuid


def initialize_community():
    """Initialize community posts in session state"""
    if 'community_posts' not in st.session_state:
        # Seed with example posts
        st.session_state.community_posts = [
            {
                'id': str(uuid.uuid4()),
                'username': 'PlantMaster',
                'content': 'Just planted my 10th balcony plant! Snake Plant is thriving 🪴',
                'plant_name': 'Snake Plant',
                'timestamp': '2025-11-15T10:30:00',
                'likes': 12,
                'liked_by': []
            },
            {
                'id': str(uuid.uuid4()),
                'username': 'GreenGuru',
                'content': 'My Neem tree reached Sapling stage! So excited to see it grow 🌳',
                'plant_name': 'Neem',
                'timestamp': '2025-11-15T08:15:00',
                'likes': 8,
                'liked_by': []
            },
            {
                'id': str(uuid.uuid4()),
                'username': 'Saul Goodman',
                'content': 'Started my balcony garden today with Tulsi and Mint. Any care tips?',
                'plant_name': None,
                'timestamp': '2025-11-14T18:45:00',
                'likes': 5,
                'liked_by': []
            }
        ]


def create_post(content, plant_name=None):
    """Create a new community post"""
    from user_profile import add_xp

    if not content.strip():
        st.error("Post content cannot be empty!")
        return False

    post = {
        'id': str(uuid.uuid4()),
        'username': st.session_state.user_profile['username'],
        'content': content.strip(),
        'plant_name': plant_name,
        'timestamp': datetime.now().isoformat(),
        'likes': 0,
        'liked_by': []
    }

    st.session_state.community_posts.insert(0, post)  # Add to top
    add_xp(20, "Shared your progress!")

    return True


def like_post(post_id):
    """Like a post"""
    username = st.session_state.user_profile['username']

    for post in st.session_state.community_posts:
        if post['id'] == post_id:
            if username not in post['liked_by']:
                post['likes'] += 1
                post['liked_by'].append(username)
            else:
                # Unlike
                post['likes'] -= 1
                post['liked_by'].remove(username)
            break


def get_time_ago(timestamp_str):
    """Convert timestamp to 'X hours ago' format"""
    try:
        post_time = datetime.fromisoformat(timestamp_str)
        now = datetime.now()
        diff = now - post_time

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds // 3600 > 0:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds // 60 > 0:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except:
        return "Recently"


def display_community_feed():
    """Display the community feed page"""
    st.header("🌍 Community Feed")
    st.markdown("Share your plant journey and get inspired by others!")

    # Create post section
    st.subheader("💬 Share Your Progress")

    with st.form("create_post_form", clear_on_submit=True):
        post_content = st.text_area(
            "What's growing in your garden?",
            max_chars=280,
            placeholder="Just planted my first balcony plant! 🌱",
            help="Maximum 280 characters"
        )

        # Optional: Link to a tracked plant
        tracked_plants = st.session_state.get('planted_trees', [])
        plant_options = ["None"] + [p['name'] for p in tracked_plants]
        selected_plant = st.selectbox(
            "Link to a plant (optional):",
            plant_options
        )

        submitted = st.form_submit_button("📤 Post Update")

        if submitted:
            plant_name = None if selected_plant == "None" else selected_plant
            if create_post(post_content, plant_name):
                st.success("✅ Posted to community!")
                st.rerun()

    st.markdown("---")

    # Display feed
    st.subheader("🌱 Latest Updates")

    if not st.session_state.community_posts:
        st.info("No posts yet. Be the first to share!")
    else:
        for post in st.session_state.community_posts[:20]:  # Show latest 20
            with st.container():
                # Post header
                col1, col2 = st.columns([4, 1])
                with col1:
                    icon = "🌱" if post['username'] == st.session_state.user_profile['username'] else "👤"
                    st.markdown(f"**{icon} {post['username']}** • {get_time_ago(post['timestamp'])}")

                # Post content
                st.markdown(post['content'])

                # Plant tag
                if post['plant_name']:
                    st.caption(f"🪴 {post['plant_name']}")

                # Like button
                username = st.session_state.user_profile['username']
                is_liked = username in post.get('liked_by', [])
                like_icon = "❤️" if is_liked else "🤍"

                col_like, col_count = st.columns([1, 4])
                with col_like:
                    if st.button(like_icon, key=f"like_{post['id']}"):
                        like_post(post['id'])
                        st.rerun()
                with col_count:
                    st.caption(f"{post['likes']} like{'s' if post['likes'] != 1 else ''}")

                st.markdown("---")

    # Community stats
    with st.sidebar:
        st.markdown("### 📊 Community Stats")
        st.metric("Total Posts", len(st.session_state.community_posts))

        total_likes = sum(p['likes'] for p in st.session_state.community_posts)
        st.metric("Total Likes", total_likes)

        unique_posters = len(set(p['username'] for p in st.session_state.community_posts))
        st.metric("Active Members", unique_posters)