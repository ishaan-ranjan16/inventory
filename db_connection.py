# # import sqlite3
# # import os

# # DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")

# # def get_connection():
# #     conn = sqlite3.connect(DB_PATH)
# #     conn.row_factory = sqlite3.Row  # allows column-name access on cursor rows
# #     return conn

# # def init_db():
# #     conn = get_connection()
# #     cur = conn.cursor()
# #     cur.execute("""
# #         CREATE TABLE IF NOT EXISTS inventory (
# #             id            INTEGER PRIMARY KEY AUTOINCREMENT,
# #             brand         TEXT,
# #             model         TEXT,
# #             serial_no     TEXT,
# #             item_category TEXT,
# #             quantity      INTEGER,
# #             warranty_status TEXT,
# #             status        TEXT,
# #             hand_over_to  TEXT,
# #             issue_date    TEXT,
# #             received_from TEXT,
# #             return_date   TEXT,
# #             note          TEXT,
# #             status_2      TEXT
# #         )
# #     """)
# #     conn.commit()
# #     cur.close()
# #     conn.close()

# # # Auto-initialise on import — safe to call repeatedly (IF NOT EXISTS guard)
# # init_db()

# import sqlite3
# import os

# # Relative path setup ensuring the database file is always created in the same directory as this script
# DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")

# def get_connection():
#     # check_same_thread=False allows Streamlit's multi-threaded runner to query SQLite safely
#     conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#     conn.row_factory = sqlite3.Row  # Allows column-name access on cursor rows (e.g. row['brand'])
#     return conn

# def init_db():
#     conn = get_connection()
#     cur = conn.cursor()
    
#     # 1. Initialize Users Table for bcrypt-hashed credentials
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             email TEXT NOT NULL,
#             password TEXT NOT NULL
#         )
#     """)
    
#     # 2. Initialize Inventory Table
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS inventory (
#             id            INTEGER PRIMARY KEY AUTOINCREMENT,
#             brand         TEXT,
#             model         TEXT,
#             serial_no     TEXT,
#             item_category TEXT,
#             quantity      INTEGER,
#             warranty_status TEXT,
#             status        TEXT,
#             hand_over_to  TEXT,
#             issue_date    TEXT,
#             received_from TEXT,
#             return_date   TEXT,
#             note          TEXT,
#             status_2      TEXT
#         )
#     """)
    
#     conn.commit()
#     cur.close()
#     conn.close()

# # Auto-initialise on import — safe to call repeatedly (IF NOT EXISTS guard)
# init_db()


# import sqlite3
# import os

# # Relative path setup ensuring the database file is always created in the same directory as this script
# DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")

# def get_connection():
#     # check_same_thread=False allows Streamlit's multi-threaded runner to query SQLite safely
#     conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#     conn.row_factory = sqlite3.Row  # Allows column-name access on cursor rows (e.g. row['brand'])
#     return conn

# def init_db():
#     conn = get_connection()
#     cur = conn.cursor()
#     # 1. Initialize Users Table with an email column
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             email TEXT NOT NULL,
#             password TEXT NOT NULL
#         )
#     """)
    
#     # Check if 'email' column exists (handles migration if the table was created previously without email)
#     cur.execute("PRAGMA table_info(users)")
#     columns = [row[1] for row in cur.fetchall()]
#     if "email" not in columns:
#         cur.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
    
#     # 2. Initialize Inventory Table
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS inventory (
#             id            INTEGER PRIMARY KEY AUTOINCREMENT,
#             brand         TEXT,
#             model         TEXT,
#             serial_no     TEXT,
#             item_category TEXT,
#             quantity      INTEGER,
#             warranty_status TEXT,
#             status        TEXT,
#             hand_over_to  TEXT,
#             issue_date    TEXT,
#             received_from TEXT,
#             return_date   TEXT,
#             note          TEXT,
#             status_2      TEXT
#         )
#     """)
    
#     conn.commit()
#     cur.close()
#     conn.close()

# # Auto-initialise on import — safe to call repeatedly (IF NOT EXISTS guard)
# init_db()

# import sqlite3
# import os

# # Relative path setup ensuring the database file is always created in the same directory as this script
# DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")

# def get_connection():
#     # check_same_thread=False allows Streamlit's multi-threaded runner to query SQLite safely
#     conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#     conn.row_factory = sqlite3.Row  # Allows column-name access on cursor rows (e.g. row['brand'])
#     return conn

# def init_db():
#     conn = get_connection()
#     cur = conn.cursor()
    
#     # 1. Initialize Users Table with email and role columns
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             email TEXT NOT NULL,
#             password TEXT NOT NULL,
#             role TEXT DEFAULT 'USER'
#         )
#     """)
    
#     # Check column migrations for existing databases
#     cur.execute("PRAGMA table_info(users)")
#     columns = [row[1] for row in cur.fetchall()]
    
#     # Migration: Add email column if missing
#     if "email" not in columns:
#         cur.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
        
#     # Migration: Add role column if missing
#     if "role" not in columns:
#         cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'USER'")
    
#     # 2. Initialize Inventory Table
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS inventory (
#             id            INTEGER PRIMARY KEY AUTOINCREMENT,
#             brand         TEXT,
#             model         TEXT,
#             serial_no     TEXT,
#             item_category TEXT,
#             quantity      INTEGER,
#             warranty_status TEXT,
#             status        TEXT,
#             hand_over_to  TEXT,
#             issue_date    TEXT,
#             received_from TEXT,
#             return_date   TEXT,
#             note          TEXT,
#             status_2      TEXT
#         )
#     """)
    
#     conn.commit()
#     cur.close()
#     conn.close()

# # Auto-initialise on import — safe to call repeatedly (IF NOT EXISTS guard)
# init_db()

import os
import sqlite3

# Relative path setup ensuring DB is created in the same directory as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventory.db")

def get_connection():
    """Returns a SQLite connection configured for Streamlit and row dictionary access."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enables access by column name (e.g., row['brand'])
    # Optional: Enable foreign keys if relational constraints are added later
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes the database tables and handles lightweight schema migrations."""
    with get_connection() as conn:
        cur = conn.cursor()
        
        # 1. Initialize Users Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'USER'
            )
        """)
        
        # Schema Migrations for existing database versions
        cur.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cur.fetchall()]
        
        if "email" not in columns:
            cur.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
            
        if "role" not in columns:
            cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'USER'")
        
        # 2. Initialize Inventory Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT,
                model TEXT,
                serial_no TEXT,
                item_category TEXT,
                quantity INTEGER DEFAULT 1,
                warranty_status TEXT,
                status TEXT,
                hand_over_to TEXT,
                issue_date TEXT,
                received_from TEXT,
                return_date TEXT,
                note TEXT,
                status_2 TEXT
            )
        """)
        
        # Optional: Add indexes for frequently searched fields
        cur.execute("CREATE INDEX IF NOT EXISTS idx_inventory_serial ON inventory(serial_no)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")

# Auto-initialize database on import
init_db()