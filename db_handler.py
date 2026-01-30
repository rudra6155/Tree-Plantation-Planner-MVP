"""
Database Handler Module - Firebase Edition
Cloud-based persistence for AirCare app using Firebase Firestore
Stores user data, planted trees, watering logs, etc.
"""

import json
import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional

# Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    st.error("Firebase not installed. Run: pip install firebase-admin")
    st.stop()


# =====================================
# FIREBASE INITIALIZATION
# =====================================

def initialize_firebase():
    """Initialize Firebase app (only once)"""
    if not firebase_admin._apps:
        try:
            # Load credentials from Streamlit secrets
            firebase_creds = dict(st.secrets["firebase"])
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Firebase initialization failed: {e}")
            st.error("Make sure you've added Firebase credentials to Streamlit secrets!")
            st.stop()

    return firestore.client()


# Initialize on import
db = initialize_firebase()


# =====================================
# USER DATA FUNCTIONS
# =====================================

def save_user_data(user_id: str, data: Dict) -> bool:
    """
    Save user profile data to Firebase

    Args:
        user_id: User identifier
        data: User profile dictionary

    Returns:
        bool: Success status
    """
    try:
        data['last_updated'] = datetime.now().isoformat()
        db.collection('users').document(user_id).set(data, merge=True)
        return True
    except Exception as e:
        st.error(f"Error saving user data: {e}")
        return False


def load_user_data(user_id: str) -> Optional[Dict]:
    """
    Load user profile data from Firebase

    Args:
        user_id: User identifier

    Returns:
        dict or None: User data or None if not found
    """
    try:
        doc = db.collection('users').document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return None


# =====================================
# PLANTED TREES FUNCTIONS
# =====================================

def save_planted_trees(user_id: str, trees: List[Dict]) -> bool:
    """
    Save list of planted trees to Firebase

    Args:
        user_id: User identifier
        trees: List of tree dictionaries

    Returns:
        bool: Success status
    """
    try:
        data = {
            'trees': trees,
            'last_updated': datetime.now().isoformat()
        }
        db.collection('planted_trees').document(user_id).set(data)
        return True
    except Exception as e:
        st.error(f"Error saving planted trees: {e}")
        return False


def load_planted_trees(user_id: str) -> List[Dict]:
    """
    Load list of planted trees from Firebase

    Args:
        user_id: User identifier

    Returns:
        list: List of tree dictionaries (empty list if none found)
    """
    try:
        doc = db.collection('planted_trees').document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            return data.get('trees', [])
        return []
    except Exception as e:
        st.error(f"Error loading planted trees: {e}")
        return []


# =====================================
# WATERING LOG FUNCTIONS
# =====================================

def save_watering_log(user_id: str, plant_id: str, timestamp: str = None) -> bool:
    """
    Log a watering event for a plant in Firebase

    Args:
        user_id: User identifier
        plant_id: Plant/tree identifier
        timestamp: ISO format timestamp (defaults to now)

    Returns:
        bool: Success status
    """
    try:
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # Load existing logs
        doc = db.collection('watering_logs').document(user_id).get()
        logs = doc.to_dict() if doc.exists else {}

        # Initialize plant's log if doesn't exist
        if plant_id not in logs:
            logs[plant_id] = []

        # Add new watering event
        logs[plant_id].append({
            'timestamp': timestamp,
            'date': datetime.now().strftime('%Y-%m-%d')
        })

        # Save back to Firebase
        db.collection('watering_logs').document(user_id).set(logs)
        return True
    except Exception as e:
        st.error(f"Error saving watering log: {e}")
        return False


def load_watering_logs(user_id: str) -> Dict[str, List[Dict]]:
    """
    Load all watering logs for a user from Firebase

    Args:
        user_id: User identifier

    Returns:
        dict: Dictionary mapping plant_id to list of watering events
    """
    try:
        doc = db.collection('watering_logs').document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return {}
    except Exception as e:
        st.error(f"Error loading watering logs: {e}")
        return {}


def get_plant_watering_count(user_id: str, plant_id: str) -> int:
    """
    Get total number of times a plant has been watered

    Args:
        user_id: User identifier
        plant_id: Plant identifier

    Returns:
        int: Number of watering events
    """
    logs = load_watering_logs(user_id)
    return len(logs.get(plant_id, []))


# =====================================
# UTILITY FUNCTIONS
# =====================================

def clear_user_data(user_id: str) -> bool:
    """
    Delete all data for a user from Firebase

    Args:
        user_id: User identifier

    Returns:
        bool: Success status
    """
    try:
        db.collection('users').document(user_id).delete()
        db.collection('planted_trees').document(user_id).delete()
        db.collection('watering_logs').document(user_id).delete()
        return True
    except Exception as e:
        st.error(f"Error clearing user data: {e}")
        return False


def get_all_users() -> List[str]:
    """
    Get list of all user IDs with saved data

    Returns:
        list: List of user IDs
    """
    try:
        users = set()

        # Get users from 'users' collection
        docs = db.collection('users').stream()
        for doc in docs:
            users.add(doc.id)

        return list(users)
    except Exception as e:
        st.error(f"Error getting users: {e}")
        return []


def get_all_data_for_admin() -> Dict:
    """
    Get ALL data from Firebase (for admin use only)

    Returns:
        dict: All users, trees, and logs
    """
    try:
        all_data = {
            'users': {},
            'planted_trees': {},
            'watering_logs': {},
            'timestamp': datetime.now().isoformat()
        }

        # Get all users
        users = db.collection('users').stream()
        for user in users:
            all_data['users'][user.id] = user.to_dict()

        # Get all planted trees
        trees = db.collection('planted_trees').stream()
        for tree in trees:
            all_data['planted_trees'][tree.id] = tree.to_dict()

        # Get all watering logs
        logs = db.collection('watering_logs').stream()
        for log in logs:
            all_data['watering_logs'][log.id] = log.to_dict()

        return all_data
    except Exception as e:
        st.error(f"Error fetching admin data: {e}")
        return {}


# =====================================
# STATS FUNCTIONS (NEW - FOR ANALYTICS)
# =====================================

def get_platform_stats() -> Dict:
    """
    Get platform-wide statistics

    Returns:
        dict: Total users, trees, waterings, etc.
    """
    try:
        stats = {
            'total_users': 0,
            'total_trees': 0,
            'total_waterings': 0,
            'active_users_7d': 0,
            'timestamp': datetime.now().isoformat()
        }

        # Count users
        users = db.collection('users').stream()
        user_count = 0
        for user in users:
            user_count += 1
        stats['total_users'] = user_count

        # Count trees
        trees_docs = db.collection('planted_trees').stream()
        total_trees = 0
        for doc in trees_docs:
            data = doc.to_dict()
            total_trees += len(data.get('trees', []))
        stats['total_trees'] = total_trees

        # Count waterings
        logs = db.collection('watering_logs').stream()
        total_waterings = 0
        for log in logs:
            log_data = log.to_dict()
            for plant_id, events in log_data.items():
                if isinstance(events, list):
                    total_waterings += len(events)
        stats['total_waterings'] = total_waterings

        return stats
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        return {}


# =====================================
# MIGRATION HELPER (JSON → FIREBASE)
# =====================================

def migrate_from_json(json_data: Dict) -> bool:
    """
    Migrate data from old JSON format to Firebase

    Args:
        json_data: Dictionary containing user_id, planted_trees, watering_logs

    Returns:
        bool: Success status
    """
    try:
        user_id = json_data.get('user_id')
        if not user_id:
            st.error("No user_id found in JSON data")
            return False

        # Migrate planted trees
        if 'planted_trees' in json_data:
            save_planted_trees(user_id, json_data['planted_trees'])

        # Migrate watering logs
        if 'watering_logs' in json_data:
            logs = json_data['watering_logs']
            doc_ref = db.collection('watering_logs').document(user_id)
            doc_ref.set(logs)

        return True
    except Exception as e:
        st.error(f"Migration error: {e}")
        return False


# =====================================
# TEST CONNECTION
# =====================================

def test_firebase_connection() -> bool:
    """
    Test if Firebase connection is working

    Returns:
        bool: True if connection works
    """
    try:
        # Try to read from a test collection
        test_ref = db.collection('_test').document('connection')
        test_ref.set({'test': True, 'timestamp': datetime.now().isoformat()})
        doc = test_ref.get()
        test_ref.delete()
        return doc.exists
    except Exception as e:
        st.error(f"Firebase connection test failed: {e}")
        return False