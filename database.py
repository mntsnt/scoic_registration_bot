import sqlite3
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        phone TEXT,
        username TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    conn.commit()
    conn.close()


def create_registration(user_id, full_name, phone, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    INSERT OR REPLACE INTO registrations (user_id, full_name, phone, username, status)
    VALUES (?, ?, ?, ?, 'pending')
    """, (user_id, full_name, phone, username))

    conn.commit()
    conn.close()


def approve_registration(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("UPDATE registrations SET status='approved' WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def reject_registration(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("UPDATE registrations SET status='rejected' WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def get_registration(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM registrations WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row