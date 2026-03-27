# database.py
import sqlite3

DB_FILE = "database.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

# ---------------------------
# Create registrations table if not exists
# ---------------------------
def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            full_name TEXT,
            phone TEXT,
            username TEXT,
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# ---------------------------
# Create new registration
# ---------------------------
def create_registration(telegram_id, full_name, phone, username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO registrations (telegram_id, full_name, phone, username)
        VALUES (?, ?, ?, ?)
    """, (telegram_id, full_name, phone, username))
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
