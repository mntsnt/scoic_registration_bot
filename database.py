# database.py

import json
import logging
import os

DB_FILE = "users.json"
NOTIFICATIONS_FILE = "pending_notifications.json"

users = {}  # user_id -> user_data
pending_notifications = {}  # limited_admin_id -> list of notification messages


def load_users():
    global users
    if not os.path.exists(DB_FILE):
        users = {}
        return

    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        if not isinstance(loaded, dict):
            logging.warning("%s does not contain a valid dictionary. Reinitializing users.", DB_FILE)
            users = {}
            return

        normalized = {}
        for key, value in loaded.items():
            try:
                normalized[int(key)] = value
            except (ValueError, TypeError):
                logging.warning("Skipping invalid user_id key in %s: %r", DB_FILE, key)

        users = normalized

    except json.JSONDecodeError:
        logging.error("Failed to decode %s; file might be corrupted. Starting with empty user set.", DB_FILE)
        users = {}
    except OSError as exc:
        logging.error("Failed to load %s: %s", DB_FILE, exc)
        users = {}


def save_users():
    temp_file = DB_FILE + ".tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, DB_FILE)
    except OSError as exc:
        logging.error("Failed to save users to %s: %s", DB_FILE, exc)
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass


def add_user(user_id, name, phone, year, username=None):
    users[int(user_id)] = {
        "name": name,
        "phone": phone,
        "year": year,
        "username": username,
        "approved": False
    }
    save_users()

def get_user(user_id):
    return users.get(user_id)

def load_notifications():
    global pending_notifications
    if not os.path.exists(NOTIFICATIONS_FILE):
        pending_notifications = {}
        return

    try:
        with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        if not isinstance(loaded, dict):
            logging.warning("%s does not contain a valid dictionary. Reinitializing notifications.", NOTIFICATIONS_FILE)
            pending_notifications = {}
            return

        normalized = {}
        for key, value in loaded.items():
            try:
                normalized[int(key)] = value if isinstance(value, list) else []
            except (ValueError, TypeError):
                logging.warning("Skipping invalid admin_id key in %s: %r", NOTIFICATIONS_FILE, key)

        pending_notifications = normalized

    except json.JSONDecodeError:
        logging.error("Failed to decode %s; file might be corrupted. Starting with empty notification set.", NOTIFICATIONS_FILE)
        pending_notifications = {}
    except OSError as exc:
        logging.error("Failed to load %s: %s", NOTIFICATIONS_FILE, exc)
        pending_notifications = {}


def save_notifications():
    temp_file = NOTIFICATIONS_FILE + ".tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(pending_notifications, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, NOTIFICATIONS_FILE)
    except OSError as exc:
        logging.error("Failed to save notifications to %s: %s", NOTIFICATIONS_FILE, exc)
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass


def add_pending_notification(limited_admin_id, message):
    """Add a pending notification for a limited admin"""
    admin_id = int(limited_admin_id)
    if admin_id not in pending_notifications:
        pending_notifications[admin_id] = []
    pending_notifications[admin_id].append(message)
    save_notifications()


def get_and_clear_pending_notifications(limited_admin_id):
    """Get all pending notifications for a limited admin and clear them"""
    admin_id = int(limited_admin_id)
    notifications = pending_notifications.get(admin_id, [])
    if notifications:
        pending_notifications[admin_id] = []
        save_notifications()
    return notifications


# Load data on import
load_users()
load_notifications()