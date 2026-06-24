import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows column-name access on cursor rows
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            brand         TEXT,
            model         TEXT,
            serial_no     TEXT,
            item_category TEXT,
            quantity      INTEGER,
            warranty_status TEXT,
            status        TEXT,
            hand_over_to  TEXT,
            issue_date    TEXT,
            received_from TEXT,
            return_date   TEXT,
            note          TEXT,
            status_2      TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# Auto-initialise on import — safe to call repeatedly (IF NOT EXISTS guard)
init_db()