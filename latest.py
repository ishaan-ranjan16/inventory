import streamlit as st
import pandas as pd
from datetime import date, datetime
import io
import smtplib
import bcrypt
import time
import random
from email.message import EmailMessage
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from streamlit_smart_text_input import st_smart_text_input

# Import unified database connection module
from db_connection import get_connection

# ═══════════════════════════════════════════
# STREAMLIT CONFIG & GLOBAL CUSTOM CSS
# ═══════════════════════════════════════════
st.set_page_config(page_title="Inventory", layout="wide")

st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
    <style>
        html { zoom: 71%; }

        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            margin-top: 0rem;
            margin-bottom: -5rem;
        }

        header[data-testid="stHeader"] { display: none; }
        [data-testid="stDecoration"]   { display: none; }

        div[data-testid="stMetricValue"] { font-size: 15px; }
        div[data-testid="stMetricLabel"] { font-size: 13px; }

        div[data-testid="stVerticalBlock"]   { gap: 0.3rem !important; }
        div[data-testid="stHorizontalBlock"] { margin-bottom: 0rem; }

        span[class^="StreamlitMaterialIcon"], .material-symbols-outlined {
            font-size: 18px;
            vertical-align: middle;
        }

        .st-key-add_inv_btn button,
        .st-key-pdf_btn button,
        .st-key-excel_btn button,
        .st-key-profile_btn button,
        .st-key-manage_users_btn button,
        .st-key-logout_btn button {
            padding: 4px 10px !important;
            font-size: 13px !important;
            white-space: nowrap !important;
            height: auto !important;
        }
            
        .st-key-logout_btn button {
            background-color: #fff1f0 !important;
            color: #cf1322 !important;
            border: 1px solid #ffa39e !important;
        }

        .st-key-refresh_btn button, .st-key-user_refresh_btn button {
            padding: 4px 10px !important;
            font-size: 13px !important;
            white-space: nowrap !important;
            height: auto !important;
            width: 100% !important;
        }

        .st-key-metrics_row { margin-bottom: 1rem; }

        .st-key-header_row, .st-key-user_header_row {
            margin-bottom: 0.7rem;
            padding-bottom: 6px;
            border-bottom: 1px solid #d8dbe0;
        }

        div[class*="st-key-edit_"] button,
        div[class*="st-key-del_"] button,
        div[class*="st-key-u_edit_"] button,
        div[class*="st-key-u_del_"] button {
            padding: 2px 8px !important;
            font-size: 13px !important;
            height: auto !important;
        }

        div[class*="st-key-header_row"] div[data-testid="column"],
        div[class*="st-key-header_row"] div[data-testid="stColumn"],
        div[class*="st-key-row_"] div[data-testid="column"],
        div[class*="st-key-row_"] div[data-testid="stColumn"],
        div[class*="st-key-user_header_row"] div[data-testid="column"],
        div[class*="st-key-user_header_row"] div[data-testid="stColumn"],
        div[class*="st-key-u_row_"] div[data-testid="column"],
        div[class*="st-key-u_row_"] div[data-testid="stColumn"] {
            border-right: 1px solid #d8dbe0;
            padding-right: 8px;
        }

        div[class*="st-key-header_row"] div[data-testid="column"]:last-child,
        div[class*="st-key-header_row"] div[data-testid="stColumn"]:last-child,
        div[class*="st-key-row_"] div[data-testid="column"]:last-child,
        div[class*="st-key-row_"] div[data-testid="stColumn"]:last-child,
        div[class*="st-key-user_header_row"] div[data-testid="column"]:last-child,
        div[class*="st-key-user_header_row"] div[data-testid="stColumn"]:last-child,
        div[class*="st-key-u_row_"] div[data-testid="column"]:last-child,
        div[class*="st-key-u_row_"] div[data-testid="stColumn"]:last-child {
            border-right: none;
        }

        div[class*="st-key-row_"], div[class*="st-key-u_row_"] {
            padding-bottom: 4px;
            border-bottom: 1px solid #eef0f3;
        }

        .st-key-add_save_btn button, .st-key-edit_save_btn button {
            background-color: #1f77b4 !important;
            color: white !important;
        }

        .auth-toggle-container {
            display: flex;
            background-color: #f0f2f5;
            padding: 4px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .auth-toggle-btn {
            flex: 1;
            text-align: center;
            padding: 8px;
            cursor: pointer;
            font-weight: bold;
            border-radius: 6px;
        }
        .auth-toggle-active {
            background-color: white;
            color: #cf1322;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# ════════════════════════
# INITIALIZE SESSION STATE
# ════════════════════════
if "logged_in"             not in st.session_state: st.session_state.logged_in = False
if "username"              not in st.session_state: st.session_state.username = None
if "user_role"             not in st.session_state: st.session_state.user_role = "USER"
if "auth_mode"             not in st.session_state: st.session_state.auth_mode = "login"
if "selected_role"         not in st.session_state: st.session_state.selected_role = "USER"
if "verification_code"     not in st.session_state: st.session_state.verification_code = None
if "pending_user_data"     not in st.session_state: st.session_state.pending_user_data = None

if "active_dialog"         not in st.session_state: st.session_state.active_dialog = None
if "edit_row_data"         not in st.session_state: st.session_state.edit_row_data = None
if "delete_id"             not in st.session_state: st.session_state.delete_id = None
if "delete_label"          not in st.session_state: st.session_state.delete_label = ""
if "add_errors"            not in st.session_state: st.session_state.add_errors = {}
if "edit_errors"           not in st.session_state: st.session_state.edit_errors = {}

# User Account Management specific state variables
if "edit_user_data"        not in st.session_state: st.session_state.edit_user_data = None
if "delete_user_target"    not in st.session_state: st.session_state.delete_user_target = None
if "do_clear_user_search"  not in st.session_state: st.session_state.do_clear_user_search = False

# Helper function to clear state values when closing any dialog
def reset_dialog_state():
    st.session_state.active_dialog = None
    st.session_state.edit_row_data = None
    st.session_state.delete_id = None
    st.session_state.delete_label = ""
    st.session_state.add_errors = {}
    st.session_state.edit_errors = {}
    st.session_state.edit_user_data = None
    st.session_state.delete_user_target = None
    for k in list(st.session_state.keys()):
        if k.startswith("add_") or k.startswith("edit_"):
            st.session_state.pop(k, None)

# ═════════════════════════════════════════
# AUTHENTICATION & SECURITY ENGINE (BCRYPT)
# ═════════════════════════════════════════
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

# Ensure standard schema and seed initial default Admin if no admins exist
def init_db_schema():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Ensure tables exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'USER'
            )
        """)
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
        conn.commit()

        cur.execute("PRAGMA table_info(users)")
        cols = [c[1] for c in cur.fetchall()]
        if cols and "role" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'USER'")
            conn.commit()

        # Check if an admin exists; if not, seed a default admin user
        cur.execute("SELECT COUNT(*) FROM users WHERE UPPER(role) = 'ADMIN'")
        admin_cnt = cur.fetchone()[0]
        if admin_cnt == 0:
            default_admin_user = "admin1"
            default_admin_email = "ishaan.ranjan16@gmail.com"
            default_admin_pass = "AdminPassword123"
            hashed_pass = hash_password(default_admin_pass)
            cur.execute(
                "INSERT OR REPLACE INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                (default_admin_user, default_admin_email, hashed_pass, "ADMIN")
            )
            conn.commit()
            
        cur.close()
        conn.close()
    except Exception:
        pass

init_db_schema()

def user_exists(username: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE LOWER(username) = LOWER(?)", (username.strip(),))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

def count_admins() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE UPPER(role) = 'ADMIN'")
    cnt = cur.fetchone()[0]
    cur.close()
    conn.close()
    return cnt

def register_user(username, email, password, role):
    username_clean = username.strip()
    email_clean = email.strip().lower()
    role_clean = role.strip().upper()

    if role_clean == "ADMIN" and count_admins() >= 3:
        return False, "Maximum admin limit reached (Max 3 Admins allowed)."

    if user_exists(username_clean):
        return False, "Username is already registered."
    
    hashed_pass = hash_password(password)
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)", 
                    (username_clean, email_clean, hashed_pass, role_clean))
        conn.commit()
        cur.close()
        conn.close()
        return True, "✅ User registered successfully!"
    except Exception as e:
        return False, f"Database Error: {str(e)}"

def verify_user_login(username, password, expected_role):
    username_clean = username.strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password, role, email FROM users WHERE LOWER(username) = LOWER(?)", (username_clean,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row and verify_password(password, row[0]):
        db_role = row[1] if row[1] else "USER"
        if db_role.upper() == expected_role.upper():
            return True, row[2]
    return False, None

def reset_user_password(username, email, new_password):
    username_clean = username.strip()
    email_clean = email.strip().lower()
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE LOWER(username) = LOWER(?)", (username_clean,))
    row = cur.fetchone()
    
    if not row:
        cur.close()
        conn.close()
        return False, "Username does not exist in our system."
        
    if row[0].strip().lower() != email_clean:
        cur.close()
        conn.close()
        return False, "Provided email does not match our records for this username."
    
    new_hashed = hash_password(new_password)
    try:
        cur.execute("UPDATE users SET password = ? WHERE LOWER(username) = LOWER(?)", (new_hashed, username_clean))
        conn.commit()
        cur.close()
        conn.close()
        return True, "✅ Password updated successfully!"
    except Exception as e:
        cur.close()
        conn.close()
        return False, f"Failed updating credentials: {str(e)}"

def get_user_details(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, email, role FROM users WHERE LOWER(username) = LOWER(?)", (username.strip(),))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"username": row[0], "email": row[1], "role": row[2]}
    return None

def update_user_profile(current_username, new_username, new_email, new_password=None):
    conn = get_connection()
    cur = conn.cursor()

    if new_username.strip().lower() != current_username.lower():
        cur.execute("SELECT 1 FROM users WHERE LOWER(username) = LOWER(?)", (new_username.strip(),))
        if cur.fetchone():
            cur.close()
            conn.close()
            return False, "New username is already taken."

    try:
        if new_password and new_password.strip():
            hashed_p = hash_password(new_password.strip())
            cur.execute(
                "UPDATE users SET username = ?, email = ?, password = ? WHERE LOWER(username) = LOWER(?)",
                (new_username.strip(), new_email.strip().lower(), hashed_p, current_username)
            )
        else:
            cur.execute(
                "UPDATE users SET username = ?, email = ? WHERE LOWER(username) = LOWER(?)",
                (new_username.strip(), new_email.strip().lower(), current_username)
            )
        conn.commit()
        cur.close()
        conn.close()
        return True, "✅ Profile updated successfully!"
    except Exception as e:
        cur.close()
        conn.close()
        return False, f"Update failed: {str(e)}"

def admin_update_user_account(old_username, new_username, new_email, new_role, new_password=None):
    conn = get_connection()
    cur = conn.cursor()

    if new_username.strip().lower() != old_username.lower():
        cur.execute("SELECT 1 FROM users WHERE LOWER(username) = LOWER(?)", (new_username.strip(),))
        if cur.fetchone():
            cur.close()
            conn.close()
            return False, "Target username is already registered."

    # Prevent demoting the last admin
    cur.execute("SELECT role FROM users WHERE LOWER(username) = LOWER(?)", (old_username,))
    row = cur.fetchone()
    old_role = row[0] if row else "USER"
    
    if old_role.upper() == "ADMIN" and new_role.upper() != "ADMIN":
        if count_admins() <= 1:
            cur.close()
            conn.close()
            return False, "Cannot change role. At least one ADMIN must remain active in system."

    if new_role.upper() == "ADMIN" and old_role.upper() != "ADMIN" and count_admins() >= 3:
        cur.close()
        conn.close()
        return False, "Cannot promote to ADMIN. Maximum admin limit (3) reached."

    try:
        if new_password and new_password.strip():
            hashed_p = hash_password(new_password.strip())
            cur.execute(
                "UPDATE users SET username = ?, email = ?, role = ?, password = ? WHERE LOWER(username) = LOWER(?)",
                (new_username.strip(), new_email.strip().lower(), new_role.strip().upper(), hashed_p, old_username)
            )
        else:
            cur.execute(
                "UPDATE users SET username = ?, email = ?, role = ? WHERE LOWER(username) = LOWER(?)",
                (new_username.strip(), new_email.strip().lower(), new_role.strip().upper(), old_username)
            )
        conn.commit()
        cur.close()
        conn.close()
        return True, "✅ Account updated successfully!"
    except Exception as e:
        cur.close()
        conn.close()
        return False, f"Update failed: {str(e)}"

def fetch_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, email, role FROM users ORDER BY role ASC, username ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=["Username", "Email", "Role"])

def delete_user_account(username):
    if user_exists(username):
        user_info = get_user_details(username)
        if user_info and user_info["role"].upper() == "ADMIN" and count_admins() <= 1:
            return False, "Cannot delete user. At least one ADMIN account must remain."

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE LOWER(username) = LOWER(?)", (username.lower(),))
    conn.commit()
    cur.close()
    conn.close()
    return True, "Account deleted successfully."

# ════════════════════
# AUTOCOMPLETE & HELPERS
# ════════════════════
@st.cache_data(ttl=300)
def fetch_distinct(column):
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            f"SELECT DISTINCT {column} FROM inventory "
            f"WHERE {column} IS NOT NULL AND TRIM({column}) != ''"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [r[0] for r in rows if r[0]]
    except Exception:
        return []

def safe_date(val):
    if val is None or (isinstance(val, str) and val.strip() == ""):
        return date.today()
    if isinstance(val, str):
        val_str = val.strip()
        for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(val_str, fmt).date()
            except ValueError:
                pass
        return date.today()
    if isinstance(val, datetime):
        return val.date()
    return val if pd.notna(val) else date.today()

def _safe_date_str(val):
    if val is None:
        return None
    if isinstance(val, (datetime, date)):
        return val.strftime('%d-%m-%Y')
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        for fmt in ('%d-%m-%Y', '%Y-%m-%d'):
            try:
                d = datetime.strptime(s, fmt)
                return d.strftime('%d-%m-%Y')
            except ValueError:
                pass
        return s
    return None

# ═══════════════════════════════════
# AUTOMATED GMAIL NOTIFICATION ENGINE
# ═══════════════════════════════════
def send_gmail_notification(subject: str, body_content: str):
    try:
        sender = st.secrets["SENDER_EMAIL"]
        password = st.secrets["SENDER_PASSWORD"]
        to_field = st.secrets["NOTIFICATION_TO"]
        cc_field = st.secrets.get("NOTIFICATION_CC", "")
    except KeyError:
        return

    to_list = [e.strip() for e in to_field.split(",") if e.strip()]
    cc_list = [e.strip() for e in cc_field.split(",") if e.strip()] if cc_field else []

    if not to_list or not sender or not password:
        return

    host, port = "smtp.gmail.com", 587
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)

    msg.set_content(body_content)

    try:
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(sender, password)
            smtp.send_message(msg)
    except Exception:
        pass

def send_verification_email(email_to, code):
    try:
        sender = st.secrets["SENDER_EMAIL"]
        password = st.secrets["SENDER_PASSWORD"]
    except KeyError:
        st.error("⚠️ SENDER_EMAIL or SENDER_PASSWORD missing from secrets Configuration context.")
        return False

    msg = EmailMessage()
    msg["Subject"] = f"🔐 Security Verification Code: {code}"
    msg["From"] = sender
    msg["To"] = email_to
    msg.set_content(f"Hello,\n\nYour security authentication verification authorization code is: {code}\n\nIf you did not initiate this login workflow request context, change credentials immediately.")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender, password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed sending OTP out: {e}")
        return False

# ═════════════════════
# DATABASE CRUD ACTIONS
# ═════════════════════
def fetch_inventory():
    columns = [
        "id", "brand", "model", "serial_no", "item_category", "quantity",
        "warranty_status", "status", "hand_over_to", "issue_date",
        "received_from", "return_date", "note", "status_2"
    ]
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT id, brand, model, serial_no, item_category, quantity,
                   warranty_status, status, hand_over_to, issue_date,
                   received_from, return_date, note, status_2
            FROM inventory
            ORDER BY id DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame([tuple(r) for r in rows], columns=columns)
    except Exception:
        st.error("⚠️ Downtime Alert: Unable to connect to the inventory database. Please try again later.")
        return pd.DataFrame(columns=columns)
    
def insert_inventory(data):
    conn = get_connection()
    cur  = conn.cursor()
    clean_data       = list(data)
    clean_data[8]    = _safe_date_str(clean_data[8])
    clean_data[10]   = _safe_date_str(clean_data[10])
    cur.execute("""
        INSERT INTO inventory (
            brand, model, serial_no, item_category,
            warranty_status, quantity, status,
            hand_over_to, issue_date, received_from,
            return_date, note, status_2
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple(clean_data))
    conn.commit()
    cur.close()
    conn.close()

    fmt = lambda val: str(val).strip() if (val is not None and str(val).strip() != "") else "—"
    subject = f"➕ Inventory Registered: {fmt(clean_data[0])} ({fmt(clean_data[1])})"
    body = (
        f"Automated Notification: A new item has been checked into inventory.\n\n"
        f"• Brand: {fmt(clean_data[0])}\n"
        f"• Model: {fmt(clean_data[1])}\n"
        f"• Serial No: {fmt(clean_data[2])}\n"
        f"• Category: {fmt(clean_data[3])}\n"
        f"• Warranty Status: {fmt(clean_data[4])}\n"
        f"• Quantity: {fmt(clean_data[5])}\n"
        f"• Status: {fmt(clean_data[6])}\n"
        f"• Assigned/Handover To: {fmt(clean_data[7])}\n"
        f"• Issue Date: {fmt(clean_data[8])}\n"
        f"• Received From: {fmt(clean_data[9])}\n"
        f"• Return Date: {fmt(clean_data[10])}\n"
        f"• Note: {fmt(clean_data[11])}\n"
        f"• Status-2: {fmt(clean_data[12])}\n\n"
        f"Timestamp: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}\n"
        f"Source: Operational Inventory Engine."
    )
    send_gmail_notification(subject, body)

def update_inventory(values):
    fields_map = {
        0: "Brand", 1: "Model", 2: "Serial No", 3: "Category",
        4: "Warranty Status", 5: "Quantity", 6: "Status",
        7: "Assigned/Handover To", 8: "Issue Date", 9: "Received From",
        10: "Return Date", 11: "Note", 12: "Status-2"
    }

    conn = get_connection()
    cur  = conn.cursor()
    
    clean_values     = list(values)
    clean_values[8]  = _safe_date_str(clean_values[8])
    clean_values[10] = _safe_date_str(clean_values[10])
    record_id        = clean_values[13]

    cur.execute("""
        SELECT brand, model, serial_no, item_category, 
               warranty_status, quantity, status, hand_over_to, 
               issue_date, received_from, return_date, note, status_2 
        FROM inventory WHERE id = ?
    """, (record_id,))
    old_row = cur.fetchone()

    cur.execute("""
        UPDATE inventory
        SET brand=?, model=?, serial_no=?, item_category=?,
            warranty_status=?, quantity=?, status=?,
            hand_over_to=?, issue_date=?, received_from=?,
            return_date=?, note=?, status_2=?
        WHERE id=?
    """, tuple(clean_values))
    conn.commit()
    cur.close()
    conn.close()

    fmt = lambda val: str(val).strip() if (val is not None and str(val).strip() != "") else "—"

    changes = []
    if old_row:
        for idx in range(13):
            old_val = _safe_date_str(old_row[idx]) if idx in (8, 10) else old_row[idx]
            new_val = clean_values[idx]
            
            if str(old_val).strip() != str(new_val).strip():
                field_title = fields_map[idx]
                changes.append(f"• Title: {field_title}\n  Previous entry in {field_title}: {fmt(old_val)}\n  New entry: {fmt(new_val)}\n")

    if changes:
        modifications_log = "\n\n📋 **Modifications Detected:**\n" + "\n".join(changes)
    else:
        modifications_log = "\n\n📋 **Modifications Detected:**\n• No values were explicitly modified."

    subject = f"✏️ Inventory Record Modified - {fmt(clean_values[0])} ({fmt(clean_values[1])})"
    body = (
        f"Automated Notification: An existing asset inventory specification has been changed.\n\n"
        f"Current Record Details:\n"
        f"• Brand: {fmt(clean_values[0])}\n"
        f"• Model: {fmt(clean_values[1])}\n"
        f"• Serial No: {fmt(clean_values[2])}\n"
        f"• Category: {fmt(clean_values[3])}\n"
        f"• Warranty Status: {fmt(clean_values[4])}\n"
        f"• Quantity: {fmt(clean_values[5])}\n"
        f"• Status: {fmt(clean_values[6])}\n"
        f"• Assigned/Handover To: {fmt(clean_values[7])}\n"
        f"• Issue Date: {fmt(clean_values[8])}\n"
        f"• Received From: {fmt(clean_values[9])}\n"
        f"• Return Date: {fmt(clean_values[10])}\n"
        f"• Note: {fmt(clean_values[11])}\n"
        f"• Status-2: {fmt(clean_values[12])}"
        f"{modifications_log}\n\n"
        f"Timestamp: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}\n"
        f"Source: Operational Inventory Engine."
    )
    
    send_gmail_notification(subject, body)

def delete_inventory(row_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM inventory WHERE id=?", (row_id,))
    conn.commit()
    cur.close()
    conn.close()

# ═════════════════════
# EXPORTS - EXCEL & PDF
# ═════════════════════
def generate_inventory_excel(data: pd.DataFrame) -> bytes:
    buffer    = io.BytesIO()
    export_df = data.reset_index(drop=True).copy()
    columns   = [
        "brand", "model", "serial_no", "item_category", "quantity",
        "warranty_status", "status", "hand_over_to", "issue_date",
        "received_from", "return_date", "note", "status_2",
    ]
    headers = [
        "S.No", "Brand", "Model", "Serial No", "Category", "Quantity",
        "Warranty", "Status", "Handover To", "Issue Date",
        "Received From", "Return Date", "Note", "Status-2",
    ]
    export_df = export_df[columns]
    export_df.insert(0, "s_no", export_df.index + 1)
    export_df.columns = headers
    export_df = export_df.fillna("—").replace("", "—")
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Inventory")
        ws = writer.sheets["Inventory"]
        for i, col in enumerate(export_df.columns):
            max_len = max(
                export_df[col].astype(str).map(len).max() if not export_df.empty else 0,
                len(str(col))
            ) + 2
            col_letter = chr(65 + i) if i < 26 else "A" + chr(65 + i - 26)
            ws.column_dimensions[col_letter].width = max_len
    buffer.seek(0)
    return buffer.getvalue()

def generate_inventory_pdf(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        leftMargin=10*mm, rightMargin=10*mm,
        topMargin=12*mm,  bottomMargin=12*mm,
    )
    styles   = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Inventory Report", styles["Title"]))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 10))
    data    = data.reset_index(drop=True)
    columns = [
        "brand", "model", "serial_no", "item_category", "quantity",
        "warranty_status", "status", "hand_over_to", "issue_date",
        "received_from", "return_date", "note", "status_2",
    ]
    headers = [
        "S.No", "Brand", "Model", "Serial No", "Category", "Quantity",
        "Warranty", "Status", "Handover To", "Issue Date",
        "Received From", "Return Date", "Note", "Status-2",
    ]
    table_data = [headers]
    for idx, row in data.iterrows():
        line = [str(idx + 1)]
        for col in columns:
            val = row.get(col, "")
            line.append(
                str(val) if val is not None and val != ""
                and (not isinstance(val, float) or not pd.isna(val))
                else "—"
            )
        table_data.append(line)
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  colors.HexColor("#2C3E50")),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTSIZE",     (0, 0), (-1, -1), 7),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F7")]),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# Scrollbar visual fixes
st.markdown("""
    <style>
    div[data-testid="stDialog"] *::-webkit-scrollbar       { width: 10px; }
    div[data-testid="stDialog"] *::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    div[data-testid="stDialog"] *::-webkit-scrollbar-thumb { background: linear-gradient(180deg,#4CAF50,#2196F3); border-radius: 10px; }
    div[data-testid="stDialog"] *::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg,#45a049,#1976D2); }
    div[data-testid="stDialog"] { scrollbar-width: thin; scrollbar-color: #2196F3 #f1f1f1; }
    </style>
""", unsafe_allow_html=True)

# ════════════
# VALIDATION
# ════════════
def validate_inventory(data):
    errors = {}
    if not (data.get("brand") or "").strip():
        errors["brand"]  = "Brand is required."
    if not (data.get("model") or "").strip():
        errors["model"]  = "Model is required."
    if not (data.get("serial") or "").strip():
        errors["serial"] = "Serial No. is required."
    return errors

def _resolve(value_key: str, native_key: str) -> str:
    ss = st.session_state
    if value_key in ss and ss[value_key] is not None:
        return str(ss[value_key]).strip()
    val = ss.get(native_key, "")
    return str(val).strip() if val is not None else ""

# ═════════════════════════════
# VIEW / UPDATE PROFILE DIALOG
# ═════════════════════════════
@st.dialog("👤 User Profile")
def view_profile_dialog():
    user_info = get_user_details(st.session_state.username)
    if not user_info:
        st.error("Failed to load user profile details.")
        return

    st.markdown(f"**Current Role:** `{user_info['role']}`")
    st.divider()
    st.markdown(f"**Username:** `{user_info['username']}`")
    st.markdown(f"**Email:** `{user_info['email']}`")
    st.divider()
    st.write("#### ✏️ Edit/Update Profile Details")
    u_name = st.text_input("Username", value=user_info["username"], key="prof_uname")
    u_email = st.text_input("Email Address", value=user_info["email"], key="prof_email")
    u_pass = st.text_input("New Password (leave blank to keep current/old password)", type="password", key="prof_pass")

    c1, c2 = st.columns(2)
    if c1.button("💾 Save Profile Changes", type="primary", use_container_width=True):
        if not u_name.strip() or not u_email.strip():
            st.toast("⚠️ Username and Email cannot be empty.")
        else:
            success, msg = update_user_profile(
                st.session_state.username, 
                u_name, 
                u_email, 
                u_pass if u_pass.strip() else None
            )
            if success:
                st.success(msg)
                st.session_state.username = u_name.strip()
                time.sleep(0.8)
                reset_dialog_state()
                st.rerun()
            else:
                st.error(msg)

    if c2.button("❌ Close", use_container_width=True):
        reset_dialog_state()
        st.rerun()

# Check and reset dialog state if user closed dialog using top-right 'X' icon
if st.session_state.active_dialog and not st.session_state.get(f"dialog_open_{st.session_state.active_dialog}", True):
    reset_dialog_state()
    st.rerun()

# ═══════════════════════════
# MANAGE USERS DIALOG (ADMIN)
# ═══════════════════════════
@st.dialog("⚙️ Manage Admin/User Accounts", width="large")
def manage_users_dialog():
    st.session_state["dialog_open_manage_users"] = True
    def sm_txt(v):
        return f'<p style="font-size:12px;margin:0">{v}</p>'

    # Sub-view: Edit Existing User
    if st.session_state.edit_user_data:
        target_u = st.session_state.edit_user_data
        st.subheader(f"✏️ Edit Account: {target_u['username']}")
        
        e_uname = st.text_input("Username", value=target_u["username"], key="m_edit_uname")
        e_email = st.text_input("Email Address", value=target_u["email"], key="m_edit_email")
        
        role_opts = ["USER", "ADMIN"]
        curr_role_idx = 1 if target_u["role"].upper() == "ADMIN" else 0
        
        e_role = st.selectbox("Role", options=role_opts, index=curr_role_idx, key="m_edit_role")
        e_pass = st.text_input("New Password (optional)\n[Leave blank to keep current password]", type="password", key="m_edit_pass")
        
        bc1, bc2 = st.columns(2)
        if bc1.button("💾 Save Changes", type="primary", use_container_width=True):
            if not e_uname.strip() or not e_email.strip():
                st.error("⚠️ Username and Email are required.")
            else:
                succ, msg = admin_update_user_account(
                    target_u["username"],
                    e_uname,
                    e_email,
                    e_role,
                    e_pass if e_pass.strip() else None
                )
                if succ:
                    st.success(msg)
                    if target_u["username"].lower() == st.session_state.username.lower():
                        st.session_state.username = e_uname.strip()
                        st.session_state.user_role = e_role.upper()
                    st.session_state.edit_user_data = None
                    time.sleep(0.6)
                    st.rerun()
                else:
                    st.error(msg)
                    
        if bc2.button("❌ Cancel", use_container_width=True):
            st.session_state.edit_user_data = None
            st.rerun()
            
        return

    # Sub-view: Confirm Delete User
    if st.session_state.delete_user_target:
        del_u = st.session_state.delete_user_target
        st.warning(f"Are you sure you want to delete account: **{del_u}**?")
        st.caption("This action cannot be undone.")
        
        dc1, dc2 = st.columns(2)
        if dc1.button("🗑️ Yes, Delete Account", type="primary", use_container_width=True):
            succ, msg = delete_user_account(del_u)
            if succ:
                st.success(f"✅ {msg}")
                st.session_state.delete_user_target = None
                time.sleep(0.6)
                st.rerun()
            else:
                st.error(f"⚠️ {msg}")
                
        if dc2.button("❌ Cancel", use_container_width=True):
            st.session_state.delete_user_target = None
            st.rerun()
            
        return

    # Handle clear search flag cleanly prior to widget instantiation
    if st.session_state.do_clear_user_search:
        st.session_state.user_search_query = ""
        st.session_state.do_clear_user_search = False

    # Main View: Account Overview List & Creation
    st.badge("**:material/inventory: Existing Accounts**", color="green")

    df_users = fetch_all_users()

    # Search + Refresh controls
    sc1, sc2 = st.columns([0.6, 0.13], vertical_alignment="bottom", gap="small")
    with sc1:
        search_q = st.text_input(
            "Search Users",
            placeholder="Search by username, email, role...",
            icon=":material/search:",
            key="user_search_query",
            label_visibility="collapsed"
        )
    with sc2:
        if st.button("Refresh", icon=":material/refresh:", key="user_refresh_btn", use_container_width=True):
            st.session_state.do_clear_user_search = True
            st.rerun()

    # Filter dataframe based on search
    if search_q and search_q.strip():
        q = search_q.strip().lower()
        df_users = df_users[
            df_users["Username"].astype(str).str.lower().str.contains(q) |
            df_users["Email"].astype(str).str.lower().str.contains(q) |
            df_users["Role"].astype(str).str.lower().str.contains(q)
        ]

    df_users = df_users.reset_index(drop=True)

    # Custom Table Header (Matching Inventory Grid Design)
    U_COL_WIDTHS = [1.0, 2.2, 3.5, 1.8, 0.8, 0.8]
    
    with st.container(key="user_header_row"):
        uh0, uh1, uh2, uh3, uh4, uh5 = st.columns(U_COL_WIDTHS, gap="small")
        uh0.badge("S.No")
        uh1.badge("Username")
        uh2.badge("Email")
        uh3.badge("Role")
        uh4.badge("Edit")
        uh5.badge("Del.")

    # Render User List Rows
    if not df_users.empty:
        for idx, urow in df_users.iterrows():
            uname_val = urow["Username"]
            email_val = urow["Email"]
            role_val  = urow["Role"]
            
            with st.container(key=f"u_row_{idx}"):
                uc0, uc1, uc2, uc3, uc4, uc5 = st.columns(U_COL_WIDTHS, gap="small")
                
                uc0.markdown(sm_txt(idx + 1),   unsafe_allow_html=True)
                uc1.markdown(sm_txt(uname_val), unsafe_allow_html=True)
                uc2.markdown(sm_txt(email_val), unsafe_allow_html=True)
                uc3.markdown(sm_txt(role_val),  unsafe_allow_html=True)
                
                if uc4.button("✏️", key=f"u_edit_{idx}"):
                    st.session_state.edit_user_data = {"username": uname_val, "email": email_val, "role": role_val}
                    st.rerun()
                    
                if uc5.button(":material/delete:", key=f"u_del_{idx}"):
                    st.session_state.delete_user_target = uname_val
                    st.rerun()
    else:
        st.info("No matching account records found.")

    st.divider()
    st.subheader("➕ Create New Account (Admin/User)")
    
    admins_count = count_admins()
    st.caption(f"Current Admin count: **{admins_count}/3**")

    c1, c2 = st.columns(2)
    new_uname = c1.text_input("Username *", key="admin_add_uname")
    new_email = c2.text_input("Email Address *", key="admin_add_email")
    
    c3, c4 = st.columns(2)
    new_pass = c3.text_input("Password *", type="password", key="admin_add_pass")
    
    role_options = ["USER"]
    if admins_count < 3:
        role_options.append("ADMIN")
    else:
        c4.caption("⚠️ Admin limit (3) reached. Only USER accounts can be created.")

    new_role = c4.selectbox("Select Role", options=role_options, key="admin_add_role")

    mc1, mc2 = st.columns(2)
    if mc1.button(":material/account_circle: Create Account", type="primary", use_container_width=True):
        if not new_uname or not new_email or not new_pass:
            st.error("⚠️ All fields are required.")
        else:
            succ, msg = register_user(new_uname, new_email, new_pass, new_role)
            if succ:
                st.success(msg)
                time.sleep(0.8)
                st.rerun()
            else:
                st.error(msg)

    if mc2.button("❌ Cancel", use_container_width=True, key="admin_add_cancel"):
        reset_dialog_state()
        st.rerun()

# ════════════════════
# ADD INVENTORY DIALOG
# ════════════════════
@st.dialog("📝 Add Inventory", width="large")
def add_inventory_dialog():
    st.session_state["dialog_open_add"] = True
    errors = st.session_state.add_errors or {}

    brand_options    = fetch_distinct("brand")
    model_options    = fetch_distinct("model")
    serial_options   = fetch_distinct("serial_no")
    warranty_options = fetch_distinct("warranty_status")
    status_options   = fetch_distinct("status")
    received_options = fetch_distinct("received_from")

    if errors:
        st.markdown(
            ":orange-badge[⚠️ Please fill in all required fields marked with * before saving.]"
        )

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)

    with r1c1:
        st.markdown("Brand <span style='color:red'>*</span>", unsafe_allow_html=True)
        brand_input = st_smart_text_input(
            label="",
            options=brand_options,
            placeholder="Brand",
            key="add_brand"
        )
        if brand_input is not None:
            st.session_state["add_brand_value"] = brand_input

        if "brand" in errors:
            st.markdown(f"<p style='color:red; font-size:13px;'>{errors['brand']}</p>", unsafe_allow_html=True)

    with r1c2:
        st.markdown("Category")
        st.markdown("<div style='margin-top: 34px;'></div>", unsafe_allow_html=True)
        st.text_input("", value=st.session_state.get("add_category", "Laptop"), key="add_category", label_visibility="collapsed")

    with r1c3:
        st.markdown("Model <span style='color:red'>*</span>", unsafe_allow_html=True)
        model_input = st_smart_text_input(
            label="",
            options=model_options,
            placeholder="Model",
            key="add_model"
        )
        if model_input is not None:
            st.session_state["add_model_value"] = model_input

        if "model" in errors:
            st.markdown(f"<p style='color:red; font-size:13px;'>{errors['model']}</p>", unsafe_allow_html=True)

    with r1c4:
        st.markdown("Serial No. <span style='color:red'>*</span>", unsafe_allow_html=True)
        serial_input = st_smart_text_input(
            label="",
            options=serial_options,
            placeholder="S No.",
            key="add_serial"
        )
        if serial_input is not None:
            st.session_state["add_serial_value"] = serial_input

        if "serial" in errors:
            st.markdown(f"<p style='color:red; font-size:13px;'>{errors['serial']}</p>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)

    with r2c1:
        st.number_input("Quantity", min_value=1, value=st.session_state.get("add_qty", 1), key="add_qty")

    with r2c2:
        warranty_input = st_smart_text_input(
            label="Warranty Status",
            options=warranty_options,
            placeholder="Warranty",
            key="add_warranty"
        )
        if warranty_input is not None:
            st.session_state["add_warranty_value"] = warranty_input

    with r2c3:
        status_input = st_smart_text_input(
            label="Status",
            options=status_options,
            placeholder="Status",
            key="add_status"
        )
        if status_input is not None:
            st.session_state["add_status_value"] = status_input

    with r2c4:
        st.text_input("Status-2", key="add_status2")

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

    r3c1, r3c2 = st.columns(2)

    with r3c1:
        st.text_input("Handover To", key="add_handover")

    with r3c2:
        received_input = st_smart_text_input(
            label="Received From",
            options=received_options,
            placeholder="Vendor / Person / IT",
            key="add_received"
        )
        if received_input is not None:
            st.session_state["add_received_value"] = received_input

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

    r4c1, r4c2 = st.columns(2)
    with r4c1:
        issue_type = st.radio(
            "📅 Issue Date",
            ["Set Date", "NA (not issued/in-inventory/available)"],
            horizontal=True, key="add_issue_type",
        )
        if issue_type == "Set Date":
            st.date_input(
                "Issue Date", value=date.today(),
                key="add_issue_date", label_visibility="collapsed",
            )

    with r4c2:
        return_type = st.radio(
            "📅 Return Date",
            ["Set Date", "NA (in-inventory/not returned/in-use)"],
            horizontal=True, key="add_return_type",
        )
        if return_type == "Set Date":
            st.date_input(
                "Return Date", value=date.today(),
                key="add_return_date", label_visibility="collapsed",
            )

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)
    st.text_area("📝 Note", key="add_note", height=80)

    col1, col2 = st.columns(2)
    save_clicked   = col1.button("💾 Save",   key="add_save_btn",   use_container_width=True, type="primary")
    cancel_clicked = col2.button("❌ Cancel", key="add_cancel_btn", use_container_width=True)

    if cancel_clicked:
        reset_dialog_state()
        st.rerun()

    if save_clicked:
        final_brand    = _resolve("add_brand_value",    "add_brand")
        final_model    = _resolve("add_model_value",    "add_model")
        final_serial   = _resolve("add_serial_value",   "add_serial")
        final_warranty = _resolve("add_warranty_value", "add_warranty")
        final_status   = _resolve("add_status_value",   "add_status")
        final_received = _resolve("add_received_value", "add_received")

        errors = validate_inventory({
            "brand":  final_brand,
            "model":  final_model,
            "serial": final_serial,
        })
        st.session_state.add_errors = errors

        if errors:
            st.rerun()

        _issue_type  = st.session_state.get("add_issue_type",  "NA")
        _return_type = st.session_state.get("add_return_type", "NA")

        issue_date  = st.session_state.get("add_issue_date",  None) if _issue_type  == "Set Date" else None
        return_date = st.session_state.get("add_return_date", None) if _return_type == "Set Date" else None

        insert_inventory((
            final_brand,
            final_model,
            final_serial,
            st.session_state.get("add_category", "") or "",
            final_warranty,
            st.session_state.get("add_qty", 1),
            final_status,
            st.session_state.get("add_handover", "") or "",
            issue_date,
            final_received,
            return_date,
            st.session_state.get("add_note", "") or "",
            st.session_state.get("add_status2", "") or "",
        ))

        fetch_distinct.clear()
        st.success("#### ✅ Saved Successfully!")
        reset_dialog_state()
        time.sleep(0.3)
        st.rerun()

# ═════════════════════════════════════════════════
# EDIT INVENTORY DIALOG (STANDARD INPUTS - NO SMART INPUT)
# ═════════════════════════════════════════════════
@st.dialog("✏️ Edit Inventory", width="large")
def edit_inventory_dialog():
    st.session_state["dialog_open_edit"] = True
    row = st.session_state.edit_row_data
    errors = st.session_state.edit_errors or {}

    if "edit_brand" not in st.session_state:
        st.session_state["edit_brand"] = row.get("brand") or ""
    if "edit_model" not in st.session_state:
        st.session_state["edit_model"] = row.get("model") or ""
    if "edit_serial" not in st.session_state:
        st.session_state["edit_serial"] = row.get("serial_no") or ""
    if "edit_category" not in st.session_state:
        st.session_state["edit_category"] = row.get("item_category") or ""
    if "edit_warranty" not in st.session_state:
        st.session_state["edit_warranty"] = row.get("warranty_status") or ""
    if "edit_status" not in st.session_state:
        st.session_state["edit_status"] = row.get("status") or ""
    if "edit_status2" not in st.session_state:
        st.session_state["edit_status2"] = row.get("status_2") or ""
    if "edit_handover" not in st.session_state:
        st.session_state["edit_handover"] = row.get("hand_over_to") or ""
    if "edit_received" not in st.session_state:
        st.session_state["edit_received"] = row.get("received_from") or ""
    if "edit_note" not in st.session_state:
        st.session_state["edit_note"] = row.get("note") or ""
    if "edit_qty" not in st.session_state:
        q_val = row.get("quantity")
        st.session_state["edit_qty"] = int(q_val) if (q_val is not None and str(q_val).isdigit()) else 1

    if errors:
        st.markdown(
            ":orange-badge[⚠️ Please fill in all required fields marked with * before saving.]"
        )

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)

    with r1c1:
        st.markdown("Brand <span style='color:red'>*</span>", unsafe_allow_html=True)
        st.text_input("", key="edit_brand", label_visibility="collapsed")
        if "brand" in errors:
            st.markdown(f"<p style='color:red; font-size:13px;'>{errors['brand']}</p>", unsafe_allow_html=True)

    with r1c2:
        st.markdown("Category")
        st.text_input("", key="edit_category", label_visibility="collapsed")

    with r1c3:
        st.markdown("Model <span style='color:red'>*</span>", unsafe_allow_html=True)
        st.text_input("", key="edit_model", label_visibility="collapsed")
        if "model" in errors:
            st.markdown(f"<p style='color:red; font-size:13px;'>{errors['model']}</p>", unsafe_allow_html=True)

    with r1c4:
        st.markdown("Serial No. <span style='color:red'>*</span>", unsafe_allow_html=True)
        st.text_input("", key="edit_serial", label_visibility="collapsed")
        if "serial" in errors:
            st.markdown(f"<p style='color:red; font-size:13px;'>{errors['serial']}</p>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)

    with r2c1:
        st.number_input("Quantity", min_value=1, key="edit_qty")

    with r2c2:
        st.text_input("Warranty Status", key="edit_warranty")

    with r2c3:
        st.text_input("Status", key="edit_status")

    with r2c4:
        st.text_input("Status-2", key="edit_status2")

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

    r3c1, r3c2 = st.columns(2)

    with r3c1:
        st.text_input("Handover To", key="edit_handover")

    with r3c2:
        st.text_input("Received From", key="edit_received")

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

    r4c1, r4c2 = st.columns(2)

    has_issue = bool(row.get("issue_date") and str(row.get("issue_date")).strip() not in ("", "None", "—"))
    with r4c1:
        issue_type = st.radio(
            "📅 Issue Date",
            ["Set Date", "NA (not issued/in-inventory/available)"],
            horizontal=True,
            index=0 if has_issue else 1,
            key="edit_issue_type",
        )
        if issue_type == "Set Date":
            st.date_input(
                "Issue Date",
                value=safe_date(row.get("issue_date")),
                key="edit_issue_date",
                label_visibility="collapsed",
            )

    has_return = bool(row.get("return_date") and str(row.get("return_date")).strip() not in ("", "None", "—"))
    with r4c2:
        return_type = st.radio(
            "📅 Return Date",
            ["Set Date", "NA (in-inventory/not returned/in-use)"],
            horizontal=True,
            index=0 if has_return else 1,
            key="edit_return_type",
        )
        if return_type == "Set Date":
            st.date_input(
                "Return Date",
                value=safe_date(row.get("return_date")),
                key="edit_return_date",
                label_visibility="collapsed",
            )

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)
    st.text_area("📝 Note", key="edit_note", height=80)

    c1, c2 = st.columns(2)
    save   = c1.button("💾 Save",   key="edit_save_btn", use_container_width=True, type="primary")
    cancel = c2.button("❌ Cancel", key="edit_cancel_btn", use_container_width=True)

    if cancel:
        reset_dialog_state()
        st.rerun()

    if save:
        final_brand    = st.session_state.get("edit_brand", "").strip()
        final_model    = st.session_state.get("edit_model", "").strip()
        final_serial   = st.session_state.get("edit_serial", "").strip()
        category       = st.session_state.get("edit_category", "").strip()
        final_warranty = st.session_state.get("edit_warranty", "").strip()
        final_status   = st.session_state.get("edit_status", "").strip()
        final_received = st.session_state.get("edit_received", "").strip()
        status_2       = st.session_state.get("edit_status2", "").strip()
        handover       = st.session_state.get("edit_handover", "").strip()
        note           = st.session_state.get("edit_note", "").strip()
        qty            = st.session_state.get("edit_qty", 1)

        errors = validate_inventory({
            "brand":  final_brand,
            "model":  final_model,
            "serial": final_serial,
        })
        st.session_state.edit_errors = errors

        if errors:
            st.rerun()

        _issue_type  = st.session_state.get("edit_issue_type",  "NA")
        _return_type = st.session_state.get("edit_return_type", "NA")

        issue_final  = st.session_state.get("edit_issue_date",  None) if _issue_type  == "Set Date" else None
        return_final = st.session_state.get("edit_return_date", None) if _return_type == "Set Date" else None

        update_inventory((
            final_brand, final_model, final_serial, category,
            final_warranty, qty, final_status,
            handover, issue_final,
            final_received, return_final,
            note, status_2,
            row["id"],
        ))

        fetch_distinct.clear()
        st.success("#### ✅ Updated Successfully!")
        reset_dialog_state()
        time.sleep(0.3)
        st.rerun()

# ═════════════════════
# CONFIRM DELETE DIALOG
# ═════════════════════
@st.dialog("🗑️ Confirm Delete")
def confirm_delete_dialog():
    st.session_state["dialog_open_delete"] = True
    item_id = st.session_state.delete_id
    item_label = st.session_state.delete_label
    st.warning("Are you sure you want to delete this item?")
    st.markdown(f"**Item:** {item_label}")
    st.caption("This action cannot be undone.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Yes, Delete", type="primary", use_container_width=True):
            delete_inventory(item_id)
            st.info("#### 🗑️ Deleted Successfully!")
            reset_dialog_state()
            time.sleep(0.3)
            st.rerun()
    with c2:
        if st.button("❌ Cancel", use_container_width=True):
            reset_dialog_state()
            st.rerun()

# ══════════════════════════════════════════════
# AUTHENTICATION PAGE ROUTER WITH LOGO CONTAINER
# ══════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
        <style>
            .stAppViewMain > div {
                display: flex;
                flex-direction: column;
                justify-content: center;
                min-height: 80vh;
            }
        </style>
    """, unsafe_allow_html=True)

    _, center_col, _ = st.columns([1.2, 1.2, 1.2])
    
    with center_col:
        with st.container(border=True):
            st.image(
                "vrizelogo.png", 
                caption="Inventory Operations Portal", 
                use_container_width=True
            )
            
        with st.container(border=True):
            if st.session_state.auth_mode == "login":
                st.markdown("<p style='font-size: 14px; font-weight: bold; margin-bottom: 14px;'>Login As -</p>", unsafe_allow_html=True)
                tc1, tc2 = st.columns(2)
                with tc1:
                    if st.button("USER", type="primary" if st.session_state.selected_role == "USER" else "secondary", use_container_width=True):
                        st.session_state.selected_role = "USER"
                        st.rerun()
                with tc2:
                    if st.button("ADMIN", type="primary" if st.session_state.selected_role == "ADMIN" else "secondary", use_container_width=True):
                        st.session_state.selected_role = "ADMIN"
                        st.rerun()

            # ─── MODE: LOGIN ───
            if st.session_state.auth_mode == "login":
                st.markdown(f"<h3 style='text-align: center; margin-bottom: 20px;'>🔐 Inventory - {st.session_state.selected_role} Login</h3>", unsafe_allow_html=True)
                login_user = st.text_input("**:material/person: Username**", key="login_username_field").strip()
                login_pass = st.text_input("**:material/lock: Password**", type="password", key="login_password_field")
                
                if st.button("LOGIN →", type="primary", use_container_width=True):
                    if not login_user or not login_pass:
                        st.toast("⚠️ Please fill in both fields.")
                    else:
                        is_valid, email = verify_user_login(login_user, login_pass, st.session_state.selected_role)
                        if is_valid:
                            otp_code = str(random.randint(100000, 999999))
                            st.session_state.verification_code = otp_code
                            st.session_state.pending_user_data = {
                                "username": login_user,
                                "role": st.session_state.selected_role,
                                "email": email
                            }
                            
                            if send_verification_email(email, otp_code):
                                st.toast("🛡️ Security authorization code sent to your registered email.")
                                st.session_state.auth_mode = "verify"
                                st.rerun()
                        else:
                            st.error(f"⚠️ Invalid credentials entered for access level context: {st.session_state.selected_role}.")
                        
                st.markdown("---")
                if st.button("Forgot Password?", use_container_width=True):
                    st.session_state.auth_mode = "forgot"
                    st.rerun()

            # ─── MODE: VERIFY ───
            elif st.session_state.auth_mode == "verify":
                p_data = st.session_state.pending_user_data or {"username": "User", "email": "your email", "role": "USER"}
                st.markdown(f"<h3 style='text-align: center; margin-bottom: 10px;'>Vrize Inventory</h3>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='text-align: center; color: #555;'>Check your mail inbox</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size:13px;'>Enter the verification code we just sent to <br><b>{p_data['email']}</b></p>", unsafe_allow_html=True)
                
                entered_otp = st.text_input("VERIFICATION CODE", placeholder="Enter 6-digit code", key="otp_field").strip()
                
                if st.button("Continue →", type="primary", use_container_width=True):
                    if entered_otp == st.session_state.verification_code:
                        st.session_state.logged_in = True
                        st.session_state.username = p_data["username"]
                        st.session_state.user_role = p_data["role"]
                        st.session_state.active_dialog = None
                        st.success("✅ Verification successful! Access Granted.")
            
                        st.session_state.verification_code = None
                        st.session_state.pending_user_data = None
                        st.session_state.auth_mode = "login"
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Invalid verification entry code. Check spelling or request again.")
                
                c_resend, c_back = st.columns(2)
                with c_resend:
                    if st.button("Resend email", use_container_width=True):
                        if st.session_state.verification_code and st.session_state.pending_user_data:
                            send_verification_email(st.session_state.pending_user_data["email"], st.session_state.verification_code)
                            st.toast("✅ Code re-transmitted successfully.")
                with c_back:
                    if st.button("← Back to login", use_container_width=True):
                        st.session_state.verification_code = None
                        st.session_state.pending_user_data = None
                        st.session_state.auth_mode = "login"
                        st.rerun()

            # ─── MODE: FORGOT ───
            elif st.session_state.auth_mode == "forgot":
                st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>🔄 Reset Account Password</h3>", unsafe_allow_html=True)

                if not st.session_state.get("forgot_otp_sent"):
                    st.caption("Enter your registered username and email to receive a confirmation code.")
                    reset_user = st.text_input("**:material/person: Registered Username**", key="reset_username").strip()
                    reset_email = st.text_input("**:material/email: Registered Email**", key="reset_email").strip()

                    if st.button("Send Confirmation Code →", type="primary", use_container_width=True):
                        if not reset_user or not reset_email:
                            st.toast("⚠️ Please provide both username and email.")
                        else:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("SELECT email FROM users WHERE LOWER(username) = LOWER(?)", (reset_user,))
                            row = cur.fetchone()
                            cur.close()
                            conn.close()

                            if not row:
                                st.error("Username does not exist in our system.")
                            elif row[0].strip().lower() != reset_email.lower():
                                st.error("Provided email does not match our records for this username.")
                            else:
                                otp_code = str(random.randint(100000, 999999))
                                if send_verification_email(reset_email, otp_code):
                                    st.session_state.reset_target_user = reset_user
                                    st.session_state.reset_target_email = reset_email
                                    st.session_state.reset_verification_code = otp_code
                                    st.session_state.forgot_otp_sent = True
                                    st.toast("🛡️ Confirmation code sent to your email!")
                                    st.rerun()

                elif not st.session_state.get("forgot_otp_verified"):
                    st.caption(f"Enter the 6-digit confirmation code sent to **{st.session_state.get('reset_target_email')}**")
                    entered_code = st.text_input("**:material/key: Confirmation Code**", key="reset_otp_input").strip()

                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        if st.button("Verify Code →", type="primary", use_container_width=True):
                            if entered_code == st.session_state.get("reset_verification_code"):
                                st.session_state.forgot_otp_verified = True
                                st.toast("✅ Code verified! Set your new password below.")
                                st.rerun()
                            else:
                                st.error("❌ Invalid confirmation code. Please check and try again.")
                    with col_v2:
                        if st.button("Resend Code", use_container_width=True):
                            new_otp = str(random.randint(100000, 999999))
                            st.session_state.reset_verification_code = new_otp
                            send_verification_email(st.session_state.reset_target_email, new_otp)
                            st.toast("✅ A new code has been sent.")

                else:
                    st.caption("Set a new password for your account.")
                    reset_pass = st.text_input("**:material/lock: Enter New Password**", type="password", key="reset_pass")
                    reset_confirm = st.text_input("**:material/lock: Confirm New Password**", type="password", key="reset_confirm")

                    if st.button("Update Password", type="primary", use_container_width=True):
                        if not reset_pass or not reset_confirm:
                            st.toast("⚠️ Both password fields are required.")
                        elif reset_pass != reset_confirm:
                            st.toast("⚠️ Passwords do not match!")
                        elif len(reset_pass) < 6:
                            st.toast("⚠️ Password must be at least 6 characters long.")
                        else:
                            success, msg = reset_user_password(
                                st.session_state.reset_target_user,
                                st.session_state.reset_target_email,
                                reset_pass
                            )
                            if success:
                                st.success(msg)
                                time.sleep(1)

                                for key in ["forgot_otp_sent", "forgot_otp_verified", "reset_target_user", "reset_target_email", "reset_verification_code"]:
                                    st.session_state.pop(key, None)

                                st.session_state.auth_mode = "login"
                                st.rerun()
                            else:
                                st.error(msg)

                st.markdown("---")
                if st.button("← Back to Login", use_container_width=True):
                    for key in ["forgot_otp_sent", "forgot_otp_verified", "reset_target_user", "reset_target_email", "reset_verification_code"]:
                        st.session_state.pop(key, None)
                    st.session_state.auth_mode = "login"
                    st.rerun()
                    
    st.markdown(
        """
        <div style="text-align:center; font-size:12px; color:gray; margin-top: 20px;">
            © 2026 Vrize. All rights reserved.<br>
            <span style="font-size:11px; color:#aaa;">Securely managed by DataGuard Advanced 2FA Systems. For support, contact admin@manageinventory.com</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# ═══════════════════════════════════════════
# DASHBOARD MODULES (GUARDS SECURE DATA AREA)
# ═══════════════════════════════════════════
df = fetch_inventory()
if not df.empty:
    df.columns = df.columns.str.strip().str.lower()

# TOP MENU BAR
if st.session_state.user_role == "ADMIN":
    title_col, add_col, manage_col, pdf_col, excel_col, logout_col, profile_col = st.columns(
        [4.2, 0.9, 0.96, 0.9, 0.9, 0.63, 0.3], vertical_alignment="center"
    )
else:
    title_col, add_col, pdf_col, excel_col, logout_col, profile_col = st.columns(
        [4.2, 0.9, 0.9, 0.9, 0.63, 0.3], vertical_alignment="center"
    )

with title_col:
    st.badge("**:material/inventory: Overall Inventory Status**", color="green")
    st.badge(f":material/person: Active Role: **{st.session_state.username}** ({st.session_state.user_role})", color="violet")

with add_col:
    if st.session_state.user_role == "ADMIN":
        if st.button("Add Inventory", icon=":material/add_box:", key="add_inv_btn", use_container_width=True):
            reset_dialog_state()
            st.session_state.active_dialog = "add"
            st.rerun()
    else:
        st.button("Add (Admin Only)", icon=":material/lock:", disabled=True, key="add_inv_btn_disabled", use_container_width=True)

if st.session_state.user_role == "ADMIN":
    with manage_col:
        if st.button("Manage Accounts", icon=":material/group:", key="manage_users_btn", use_container_width=True):
            reset_dialog_state()
            st.session_state.active_dialog = "manage_users"
            st.rerun()

with pdf_col:
    pdf_bytes = generate_inventory_pdf(df)
    st.download_button(
        label=":material/download: Download PDF",
        data=pdf_bytes,
        file_name=f"inventory-report_{date.today().strftime('%d-%m-%Y')}.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="pdf_btn",
    )

with excel_col:
    excel_bytes = generate_inventory_excel(df)
    st.download_button(
        label=":material/description: Download Excel",
        data=excel_bytes,
        file_name=f"inventory-report_{date.today().strftime('%d-%m-%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="excel_btn",
    )

with logout_col:
    if st.button("Log Out", icon=":material/logout:", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_role = "USER"
        reset_dialog_state()
        st.rerun()

with profile_col:
    if st.button("", icon=":material/account_circle:", key="profile_btn", use_container_width=True, help=""):
        reset_dialog_state()
        st.session_state.active_dialog = "profile"
        st.rerun()

# METRICS
total     = len(df)
Issued    = len(df[df["status"].str.lower().isin(["issued","given", "in use"])]) if not df.empty else 0
Available = len(df[df["status"].str.lower().isin(["in-inventory", "inventory", "available","in inventory","in stock"])]) if not df.empty else 0
Damaged   = len(df[df["status"].str.lower().isin(["damaged", "broken", "maintenance"])]) if not df.empty else 0

with st.container(key="metrics_row"):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total",       total)
    c2.metric("Issued",      Issued)
    c3.metric("In-Inventory", Available)
    c4.metric("Damaged",     Damaged)

# SEARCH + REFRESH
if st.session_state.get("do_clear_search"):
    st.session_state.search_box      = ""
    st.session_state.do_clear_search = False
    st.rerun()

COL_WIDTHS        = [0.7, 0.8, 1.2, 1.0, 0.9, 0.9, 1.3, 1.2, 1.3, 1.1, 1.5, 1.3, 1.6, 1.2, 0.6, 0.6]
SEARCH_ROW_WIDTHS = [sum(COL_WIDTHS[:14]), sum(COL_WIDTHS[14:])]

search_col, refresh_col = st.columns(SEARCH_ROW_WIDTHS, vertical_alignment="bottom", gap="small")

with search_col:
    search2 = st.text_input(
        "Search Inventory List",
        placeholder="Search by brand, model, serial no., status...",
        icon=":material/search:",
        label_visibility="collapsed",
        key="search_box",
    )

with refresh_col:
    if st.button("Refresh", icon=":material/refresh:", key="refresh_btn", use_container_width=True):
        st.session_state.do_clear_search = True
        st.rerun()

list_df = df.copy().fillna("")

if search2 and search2.strip():
    mask = list_df.astype(str).apply(
        lambda col: col.str.contains(search2, case=False, na=False, regex=False)
    ).any(axis=1)
    list_df = list_df[mask]

list_df = list_df.reset_index(drop=True)
list_df["s_no"] = list_df.index + 1

# TABLE — HEADER
with st.container(key="header_row"):
    h0,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,h13,h14,h15 = st.columns(COL_WIDTHS, gap="small")
    h0.badge("S.No");        h1.badge("Brand");          h2.badge("Model")
    h3.badge("Serial No.");  h4.badge("Category");       h5.badge("Quantity")
    h6.badge("Warranty");    h7.badge("Status");         h8.badge("Handover To")
    h9.badge("Issue Date");  h10.badge("Received From"); h11.badge("Return Date")
    h12.badge("Note");       h13.badge("Status-2");      h14.badge("Edit"); h15.badge("Del.")

# TABLE — DATA ROWS
def small(val):
    return f'<p style="font-size:12px;margin:0">{val}</p>'

def safe_val(val):
    if val is None:                             return "—"
    if isinstance(val, float) and pd.isna(val): return "—"
    if str(val).strip() == "":                  return "—"
    return val

def safe_date_str(val):
    if val is None or str(val).strip() in ("", "None", "NaT", "NAN", "NaN"):
        return "—"
    return str(val)

for _, row in list_df.iterrows():
    uid = str(row["id"])

    with st.container(key=f"row_{uid}"):
        c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15 = st.columns(COL_WIDTHS, gap="small")

        c0.markdown( small(safe_val(row["s_no"])),             unsafe_allow_html=True)
        c1.markdown( small(safe_val(row["brand"])),              unsafe_allow_html=True)
        c2.markdown( small(safe_val(row["model"])),              unsafe_allow_html=True)
        c3.markdown( small(safe_val(row["serial_no"])),          unsafe_allow_html=True)
        c4.markdown( small(safe_val(row["item_category"])),      unsafe_allow_html=True)
        c5.markdown( small(safe_val(row["quantity"])),           unsafe_allow_html=True)
        c6.markdown( small(safe_val(row["warranty_status"])),    unsafe_allow_html=True)
        c7.markdown( small(safe_val(row["status"])),             unsafe_allow_html=True)
        c8.markdown( small(safe_val(row.get("hand_over_to"))),   unsafe_allow_html=True)
        c9.markdown( small(safe_date_str(row["issue_date"])),    unsafe_allow_html=True)
        c10.markdown(small(safe_val(row.get("received_from"))),  unsafe_allow_html=True)
        c11.markdown(small(safe_date_str(row["return_date"])),   unsafe_allow_html=True)
        c12.markdown(small(safe_val(row.get("note"))),           unsafe_allow_html=True)
        c13.markdown(small(safe_val(row.get("status_2"))),       unsafe_allow_html=True)

        if st.session_state.user_role == "ADMIN":
            if c14.button("✏️", key=f"edit_{uid}"):
                reset_dialog_state()
                st.session_state.edit_row_data  = row.to_dict()
                st.session_state.active_dialog  = "edit"
                st.rerun()

            if c15.button(":material/delete:", key=f"del_{uid}"):
                reset_dialog_state()
                brand_val  = safe_val(row["brand"])
                model_val  = safe_val(row["model"])
                serial_val = safe_val(row["serial_no"])
                st.session_state.delete_id     = row["id"]
                st.session_state.delete_label  = f"{brand_val} — {model_val} (S/No: {serial_val})"
                st.session_state.active_dialog = "delete"
                st.rerun()
        else:
            c14.write("🔒")
            c15.write("🔒")

# SINGLE DIALOG DISPATCHER
if st.session_state.active_dialog == "add":
    add_inventory_dialog()
elif st.session_state.active_dialog == "edit":
    edit_inventory_dialog()
elif st.session_state.active_dialog == "delete":
    confirm_delete_dialog()
elif st.session_state.active_dialog == "profile":
    view_profile_dialog()
elif st.session_state.active_dialog == "manage_users":
    manage_users_dialog()

st.divider()
st.caption("Inventory Management System • Dashboard")