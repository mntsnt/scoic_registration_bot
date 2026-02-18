# database.py
import sqlite3

DB_FILE = "database.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

# ---------------------------
# Create orders table if not exists
# ---------------------------
def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            order_id TEXT,
            amount REAL,
            status TEXT,
            proof TEXT,
            full_name TEXT,
            phone TEXT,
            username TEXT
        )
    """)
    conn.commit()
    conn.close()

# ---------------------------
# Create new order
# ---------------------------
def create_order(telegram_id, order_id, amount, full_name=None, phone=None, username=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (telegram_id, order_id, amount, status, full_name, phone, username)
        VALUES (?, ?, ?, 'PENDING', ?, ?, ?)
    """, (telegram_id, order_id, amount, full_name, phone, username))
    conn.commit()
    conn.close()

# ---------------------------
# Add proof (text or photo file_id)
# ---------------------------
def add_proof(order_id, proof):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE orders SET proof=? WHERE order_id=?", (proof, order_id))
    conn.commit()
    conn.close()

# ---------------------------
# Approve order
# ---------------------------
def mark_approved(order_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE orders SET status='APPROVED' WHERE order_id=?", (order_id,))
    conn.commit()
    conn.close()

# ---------------------------
# Reject order
# ---------------------------
def mark_rejected(order_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE orders SET status='REJECTED' WHERE order_id=?", (order_id,))
    conn.commit()
    conn.close()

# ---------------------------
# Fetch single order by order_id
# ---------------------------
def get_order(order_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE order_id=?", (order_id,))
    order = c.fetchone()
    conn.close()
    return order

# ---------------------------
# Fetch latest pending order for a user
# ---------------------------
def get_latest_pending_order(telegram_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM orders
        WHERE telegram_id=? AND status='PENDING'
        ORDER BY id DESC LIMIT 1
    """, (telegram_id,))
    order = c.fetchone()
    conn.close()
    return order

# Initialize DB on import
init_db()
