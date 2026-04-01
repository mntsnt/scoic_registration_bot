# database.py

import json
import logging
import os

DB_FILE = "users.json"

users = {}  # user_id -> user_data


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

def approve_user(user_id):
    user_id = int(user_id)
    if user_id in users:
        users[user_id]["approved"] = True
        save_users()
        return True
    return False


# Load users on import
load_users()