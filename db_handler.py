"""
Database Handler Module
Simple JSON-based persistence for AirCare app
Stores user data, planted trees, watering logs, etc.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Create data directory if it doesn't exist
DATA_DIR = "aircare_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# =====================================
# HELPER FUNCTIONS
# =====================================

def _get_file_path(user_id: str, data_type: str) -> str:
    """
    Generate file path for user data

    Args:
        user_id: Unique user identifier
        data_type: Type of data (e.g., 'profile', 'trees', 'logs')

    Returns:
        str: Full file path
    """
    return os.path.join(DATA_DIR, f"{user_id}_{data_type}.json")


def _load_json(file_path: str) -> Optional[Dict]:
    """
    Load JSON data from file

    Args:
        file_path: Path to JSON file

    Returns:
        dict or None: Loaded data or None if file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return None


def _save_json(file_path: str, data: Dict) -> bool:
    """
    Save data to JSON file

    Args:
        file_path: Path to JSON file
        data: Dictionary to save

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False


# =====================================
# USER DATA FUNCTIONS
# =====================================

def save_user_data(user_id: str, data: Dict) -> bool:
    """
    Save user profile data

    Args:
        user_id: User identifier (e.g., email or session ID)
        data: User profile dictionary

    Returns:
        bool: Success status

    Example:
        user_data = {
            'name': 'John Doe',
            'location': 'Mumbai',
            'preferences': {...}
        }
        save_user_data('user123', user_data)
    """
    file_path = _get_file_path(user_id, 'profile')
    data['last_updated'] = datetime.now().isoformat()
    return _save_json(file_path, data)


def load_user_data(user_id: str) -> Optional[Dict]:
    """
    Load user profile data

    Args:
        user_id: User identifier

    Returns:
        dict or None: User data or None if not found
    """
    file_path = _get_file_path(user_id, 'profile')
    return _load_json(file_path)


# =====================================
# PLANTED TREES FUNCTIONS
# =====================================

def save_planted_trees(user_id: str, trees: List[Dict]) -> bool:
    """
    Save list of planted trees

    Args:
        user_id: User identifier
        trees: List of tree dictionaries

    Returns:
        bool: Success status

    Example:
        trees = [
            {
                'id': 'tree_001',
                'name': 'Snake Plant',
                'planted_date': '2025-01-15',
                'status': 'Healthy'
            }
        ]
        save_planted_trees('user123', trees)
    """
    file_path = _get_file_path(user_id, 'trees')
    data = {
        'trees': trees,
        'last_updated': datetime.now().isoformat()
    }
    return _save_json(file_path, data)


def load_planted_trees(user_id: str) -> List[Dict]:
    """
    Load list of planted trees

    Args:
        user_id: User identifier

    Returns:
        list: List of tree dictionaries (empty list if none found)
    """
    file_path = _get_file_path(user_id, 'trees')
    data = _load_json(file_path)

    if data and 'trees' in data:
        return data['trees']
    return []


# =====================================
# WATERING LOG FUNCTIONS
# =====================================

def save_watering_log(user_id: str, plant_id: str, timestamp: str = None) -> bool:
    """
    Log a watering event for a plant

    Args:
        user_id: User identifier
        plant_id: Plant/tree identifier
        timestamp: ISO format timestamp (defaults to now)

    Returns:
        bool: Success status

    Example:
        save_watering_log('user123', 'tree_001')
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    file_path = _get_file_path(user_id, 'watering_logs')
    logs = _load_json(file_path) or {}

    # Initialize plant's log if doesn't exist
    if plant_id not in logs:
        logs[plant_id] = []

    # Add new watering event
    logs[plant_id].append({
        'timestamp': timestamp,
        'date': datetime.now().strftime('%Y-%m-%d')
    })

    return _save_json(file_path, logs)


def load_watering_logs(user_id: str) -> Dict[str, List[Dict]]:
    """
    Load all watering logs for a user

    Args:
        user_id: User identifier

    Returns:
        dict: Dictionary mapping plant_id to list of watering events

    Example:
        {
            'tree_001': [
                {'timestamp': '2025-01-15T10:30:00', 'date': '2025-01-15'},
                {'timestamp': '2025-01-17T10:30:00', 'date': '2025-01-17'}
            ]
        }
    """
    file_path = _get_file_path(user_id, 'watering_logs')
    return _load_json(file_path) or {}


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
    Delete all data for a user (useful for reset feature)

    Args:
        user_id: User identifier

    Returns:
        bool: Success status
    """
    try:
        data_types = ['profile', 'trees', 'watering_logs']
        for data_type in data_types:
            file_path = _get_file_path(user_id, data_type)
            if os.path.exists(file_path):
                os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error clearing data for {user_id}: {e}")
        return False


def get_all_users() -> List[str]:
    """
    Get list of all user IDs with saved data

    Returns:
        list: List of user IDs
    """
    try:
        users = set()
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.json'):
                # Extract user_id from filename (format: user_id_datatype.json)
                user_id = filename.split('_')[0]
                users.add(user_id)
        return list(users)
    except Exception as e:
        print(f"Error getting users: {e}")
        return []


# =====================================
# EXAMPLE USAGE (FOR TESTING)
# =====================================

if __name__ == "__main__":
    # Test the functions
    print("Testing db_handler...")

    # Test user data
    test_user = "test_user_123"
    test_data = {
        'name': 'Test User',
        'location': 'Mumbai',
        'email': 'test@example.com'
    }

    print("\n1. Saving user data...")
    save_user_data(test_user, test_data)

    print("2. Loading user data...")
    loaded_data = load_user_data(test_user)
    print(f"   Loaded: {loaded_data}")

    # Test planted trees
    print("\n3. Saving planted trees...")
    test_trees = [
        {
            'id': 'tree_001',
            'name': 'Snake Plant',
            'planted_date': '2025-01-15',
            'status': 'Healthy'
        },
        {
            'id': 'tree_002',
            'name': 'Tulsi',
            'planted_date': '2025-01-16',
            'status': 'Growing'
        }
    ]
    save_planted_trees(test_user, test_trees)

    print("4. Loading planted trees...")
    loaded_trees = load_planted_trees(test_user)
    print(f"   Loaded {len(loaded_trees)} trees")

    # Test watering logs
    print("\n5. Logging watering events...")
    save_watering_log(test_user, 'tree_001')
    save_watering_log(test_user, 'tree_001')
    save_watering_log(test_user, 'tree_002')

    print("6. Loading watering logs...")
    logs = load_watering_logs(test_user)
    print(f"   Tree 001 watered {len(logs.get('tree_001', []))} times")
    print(f"   Tree 002 watered {len(logs.get('tree_002', []))} times")

    print("\n7. Getting all users...")
    all_users = get_all_users()
    print(f"   Found users: {all_users}")

    print("\n✅ All tests completed!")
    print(f"   Data stored in: {os.path.abspath(DATA_DIR)}")