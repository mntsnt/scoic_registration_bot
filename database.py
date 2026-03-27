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
            status TEXT DEFAULT 'PENDING',
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
        INSERT INTO registrations (telegram_id, full_name, phone, username, status)
        VALUES (?, ?, ?, ?, 'PENDING')
    """, (telegram_id, full_name, phone, username))
    conn.commit()
    conn.close()

# ---------------------------
# Approve registration
# ---------------------------
def approve_registration(registration_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE registrations SET status='APPROVED' WHERE id=?", (registration_id,))
    conn.commit()
    conn.close()

# ---------------------------
# Reject registration
# ---------------------------
def reject_registration(registration_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE registrations SET status='REJECTED' WHERE id=?", (registration_id,))
    conn.commit()
    conn.close()

# ---------------------------
# Get pending registrations
# ---------------------------
def get_pending_registrations():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM registrations WHERE status='PENDING' ORDER BY registered_at ASC")
    registrations = c.fetchall()
    conn.close()
    return registrations

# ---------------------------
# Get registration by id
# ---------------------------
def get_registration(registration_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM registrations WHERE id=?", (registration_id,))
    registration = c.fetchone()
    conn.close()
    return registration

# Initialize DB on import
init_db()
