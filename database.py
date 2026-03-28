# database.py

import json
import os

DB_FILE = "users.json"

users = {}  # user_id -> user_data

def load_users():
    global users
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            users = json.load(f)

def save_users():
    with open(DB_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def add_user(user_id, name, phone, username=None):
    users[user_id] = {
        "name": name,
        "phone": phone,
        "username": username,
        "approved": False
    }
    save_users()

def get_user(user_id):
    return users.get(user_id)

def approve_user(user_id):
    if user_id in users:
        users[user_id]["approved"] = True
        save_users()

# Load users on import
load_users()