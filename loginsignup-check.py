import streamlit as st
import pandas as pd
from datetime import date, datetime
import io
import time
import hashlib
from db_connection import get_connection
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from streamlit_smart_text_input import st_smart_text_input

# ═══════════════════════════════════════════════════════════════════
# INITIALIZATION & PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Inventory Management", layout="wide")

# ═══════════════════════════════════════════════════════════════════
# DATABASE USER TABLE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════
def init_user_db():
    """Ensures the users table exists for handling local signups."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Supporting standard SQL syntax compatible with SQLite / SQLite3 / MySQL variants
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        
        # Seed a default admin account if table is completely empty
        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            default_hash = hashlib.sha256("admin123".encode()).hexdigest()
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", default_hash))
            conn.commit()
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"User DB Init Error: {e}")

init_user_db()

# ═══════════════════════════════════════════════════════════════════
# AUTHENTICATION HELPERS
# ═══════════════════════════════════════════════════════════════════
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (username.strip(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and row[0] == hash_password(password):
            return True
        return False
    except Exception:
        return False

def create_user(username, password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username = ?", (username.strip(),))
        if cur.fetchone():
            cur.close()
            conn.close()
            return False, "⚠️ Username already exists!"
        
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username.strip(), hash_password(password)))
        conn.commit()
        cur.close()
        conn.close()
        return True, "✅ Account created successfully! Please log in."
    except Exception as e:
        return False, f"⚠️ Error creating account: {e}"

# ═══════════════════════════════════════════════════════════════════
# LOGIN & SIGN UP INTERFACE GATE
# ═══════════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # "login" or "signup"

def auth_page():
    st.markdown("""
        <style>
            header[data-testid="stHeader"] { display: none !important; }
            [data-testid="stDecoration"]   { display: none !important; }
            div[data-testid="stForm"] {
                border: 1px solid #e6e9ef;
                padding: 2rem;
                border-radius: 8px;
                background-color: #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)
    
    _, col_center, _ = st.columns([1, 1.2, 1])
    
    with col_center:
        st.write("")
        st.write("")
        
        if st.session_state.auth_mode == "login":
            st.subheader("🔑 Inventory System Login")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username...").strip()
                password = st.text_input("Password", type="password", placeholder="Enter password...")
                submit = st.form_submit_button("Log In", use_container_width=True, type="primary")
                
                if submit:
                    if username and password and verify_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.current_user = username
                        st.success("Access granted!")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error("❌ Invalid Username or Password")
            
            if st.button("New here? Create an account / Sign Up", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()
                
        else:
            st.subheader("📝 Create New Account")
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username", placeholder="Enter unique username...").strip()
                new_password = st.text_input("Choose Password", type="password", placeholder="Enter strong password...")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Retype password...")
                submit_signup = st.form_submit_button("Sign Up & Register", use_container_width=True, type="primary")
                
                if submit_signup:
                    if not new_username or not new_password:
                        st.error("❌ Fields cannot be empty.")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords do not match!")
                    elif len(new_password) < 4:
                        st.error("❌ Password must be at least 4 characters long.")
                    else:
                        success, message = create_user(new_username, new_password)
                        if success:
                            st.success(message)
                            st.session_state.auth_mode = "login"
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
                            
            if st.button("Already have an account? Go to Log In", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

# Stop layout processing if user is unauthorized
if not st.session_state.logged_in:
    auth_page()
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# MAIN APP STYLING & ASSETS (Only loaded upon successful login)
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
    <style>
        html { zoom: 69%; }

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

        .st-key-refresh_btn button {
            padding: 4px 10px !important;
            font-size: 13px !important;
            white-space: nowrap !important;
            height: auto !important;
            width: 100% !important;
        }

        .st-key-metrics_row { margin-bottom: 1rem; }

        .st-key-header_row {
            margin-bottom: 0.7rem;
            padding-bottom: 6px;
            border-bottom: 1px solid #d8dbe0;
        }

        div[class*="st-key-edit_"] button,
        div[class*="st-key-del_"] button {
            padding: 2px 8px !important;
            font-size: 13px !important;
            height: auto !important;
        }

        div[class*="st-key-header_row"] div[data-testid="column"],
        div[class*="st-key-header_row"] div[data-testid="stColumn"],
        div[class*="st-key-row_"] div[data-testid="column"],
        div[class*="st-key-row_"] div[data-testid="stColumn"] {
            border-right: 1px solid #d8dbe0;
            padding-right: 8px;
        }

        div[class*="st-key-header_row"] div[data-testid="column"]:last-child,
        div[class*="st-key-header_row"] div[data-testid="stColumn"]:last-child,
        div[class*="st-key-row_"] div[data-testid="column"]:last-child,
        div[class*="st-key-row_"] div[data-testid="stColumn"]:last-child {
            border-right: none;
        }

        div[class*="st-key-row_"] {
            padding-bottom: 4px;
            border-bottom: 1px solid #eef0f3;
        }

        .st-key-add_save_btn button {
            background-color: #1f77b4 !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SESSION STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════
if "active_dialog"  not in st.session_state: st.session_state.active_dialog  = None
if "edit_row_data"  not in st.session_state: st.session_state.edit_row_data  = None
if "delete_id"      not in st.session_state: st.session_state.delete_id      = None
if "delete_label"   not in st.session_state: st.session_state.delete_label   = ""
if "add_errors"     not in st.session_state: st.session_state.add_errors     = {}

# ═══════════════════════════════════════════════════════════════════
# AUTOCOMPLETE — DB UTILS
# ═══════════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════════
# DATE HELPERS
# ═══════════════════════════════════════════════════════════════════
def safe_date(val):
    if val is None or (isinstance(val, str) and val.strip() == ""):
        return date.today()
    if isinstance(val, str):
        try:
            return datetime.strptime(val, "%d-%m-%Y").date()
        except ValueError:
            return date.today()
    if isinstance(val, datetime):
        return val.date()
    return val if pd.notna(val) else date.today()

def _safe_date_str(val):
    if val is None:
        return None
    if isinstance(val, datetime) or isinstance(val, date):
        return val.strftime('%d-%m-%Y')
    if isinstance(val, str):
        s = val.strip()
        if not s: return None
        try:
            datetime.strptime(s, '%d-%m-%Y')
            return s
        except ValueError:
            return None
    return None

# ═══════════════════════════════════════════════════════════════════
# DATABASE CORE OPERATIONS
# ═══════════════════════════════════════════════════════════════════
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
    except Exception as e:
        print(f"CRITICAL DATABASE ERROR: {e}")
        st.error("⚠️ Downtime Alert: Unable to connect to the inventory database.")
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

def update_inventory(values):
    conn = get_connection()
    cur  = conn.cursor()
    clean_values     = list(values)
    clean_values[8]  = _safe_date_str(clean_values[8])
    clean_values[10] = _safe_date_str(clean_values[10])
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

def delete_inventory(row_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM inventory WHERE id=?", (row_id,))
    conn.commit()
    cur.close()
    conn.close()

# ═══════════════════════════════════════════════════════════════════
# EXPORTS (EXCEL & PDF)
# ═══════════════════════════════════════════════════════════════════
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
            max_len = max(export_df[col].astype(str).map(len).max() if not export_df.empty else 0, len(str(col))) + 2
            col_letter = chr(65 + i) if i < 26 else "A" + chr(65 + i - 26)
            ws.column_dimensions[col_letter].width = max_len
    buffer.seek(0)
    return buffer.getvalue()

def generate_inventory_pdf(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        leftMargin=10*mm, rightMargin=10*mm, topMargin=12*mm, bottomMargin=12*mm,
    )
    styles   = getSampleStyleSheet()
    elements = [
        Paragraph("Inventory Report", styles["Title"]),
        Paragraph(f"Generated on {datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}", styles["Normal"]),
        Spacer(1, 10)
    ]
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
    for idx, row in data.reset_index(drop=True).iterrows():
        line = [str(idx + 1)]
        for col in columns:
            val = row.get(col, "")
            line.append(str(val) if val is not None and val != "" and (not isinstance(val, float) or not pd.isna(val)) else "—")
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

# ═══════════════════════════════════════════════════════════════════
# DIALOG MODAL SCROLLBAR CUSTOMIZATION & VALIDATION
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
    <style>
    div[data-testid="stDialog"] *::-webkit-scrollbar       { width: 10px; }
    div[data-testid="stDialog"] *::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    div[data-testid="stDialog"] *::-webkit-scrollbar-thumb { background: linear-gradient(180deg,#4CAF50,#2196F3); border-radius: 10px; }
    div[data-testid="stDialog"] { scrollbar-width: thin; scrollbar-color: #2196F3 #f1f1f1; }
    </style>
""", unsafe_allow_html=True)

def validate_inventory(data):
    errors = {}
    if not (data.get("brand") or "").strip():  errors["brand"]  = "Brand is required."
    if not (data.get("model") or "").strip():  errors["model"]  = "Model is required."
    if not (data.get("serial") or "").strip(): errors["serial"] = "Serial No. is required."
    return errors

# ═══════════════════════════════════════════════════════════════════
# ADD INVENTORY DIALOG
# ═══════════════════════════════════════════════════════════════════
@st.dialog("📝 Add Inventory", width="large")
def add_inventory_dialog():
    errors = st.session_state.add_errors or {}
    
    brand_options    = fetch_distinct("brand")
    model_options    = fetch_distinct("model")
    serial_options   = fetch_distinct("serial_no")
    warranty_options = fetch_distinct("warranty_status")
    status_options   = fetch_distinct("status")
    received_options = fetch_distinct("received_from")

    if errors:
        st.markdown(":orange-badge[⚠️ Please fill in all required fields marked with * before saving.]")

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        st.markdown("Brand <span style='color:red'>*</span>", unsafe_allow_html=True)
        brand_input = st_smart_text_input(label="", options=brand_options, placeholder="Type/select brand...", key="add_brand")
        if brand_input is not None: st.session_state["add_brand_value"] = brand_input
        if "brand" in errors: st.markdown(f"<p style='color:red; font-size:13px;'>{errors['brand']}</p>", unsafe_allow_html=True)
    with r1c2:
        st.text_input("Category", value=st.session_state.get("add_category", "Laptop"), key="add_category")
    with r1c3:
        st.markdown("Model <span style='color:red'>*</span>", unsafe_allow_html=True)
        model_input = st_smart_text_input(label="", options=model_options, placeholder="Type/select...", key="add_model")
        if model_input is not None: st.session_state["add_model_value"] = model_input
        if "model" in errors: st.markdown(f"<p style='color:red; font-size:13px;'>{errors['model']}</p>", unsafe_allow_html=True)
    with r1c4:
        st.markdown("Serial No. <span style='color:red'>*</span>", unsafe_allow_html=True)
        serial_input = st_smart_text_input(label="", options=serial_options, placeholder="Type/select...", key="add_serial")
        if serial_input is not None: st.session_state["add_serial_value"] = serial_input
        if "serial" in errors: st.markdown(f"<p style='color:red; font-size:13px;'>{errors['serial']}</p>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        st.number_input("Quantity", min_value=1, value=st.session_state.get("add_qty", 1), key="add_qty")
    with r2c2:
        warranty_input = st_smart_text_input(label="Warranty Status", options=warranty_options, placeholder="Type/select...", key="add_warranty")
        if warranty_input is not None: st.session_state["add_warranty_value"] = warranty_input
    with r2c3:
        status_input = st_smart_text_input(label="Status", options=status_options, placeholder="Type/select...", key="add_status")
        if status_input is not None: st.session_state["add_status_value"] = status_input
    with r2c4:
        st.text_input("Status-2", key="add_status2")

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

    r3c1, r3c2 = st.columns(2)
    with r3c1:  st.text_input("Handover To", key="add_handover")
    with r3c2:
        received_input = st_smart_text_input(label="Received From", options=received_options, placeholder="Vendor/IT...", key="add_received")
        if received_input is not None: st.session_state["add_received_value"] = received_input

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

    r4c1, r4c2 = st.columns(2)
    with r4c1:
        issue_type = st.radio("📅 Issue Date", ["Set Date", "NA"], horizontal=True, key="add_issue_type")
        if issue_type == "Set Date": st.date_input("Issue Date", value=date.today(), key="add_issue_date", label_visibility="collapsed")
    with r4c2:
        return_type = st.radio("📅 Return Date", ["Set Date", "NA"], horizontal=True, key="add_return_type")
        if return_type == "Set Date": st.date_input("Return Date", value=date.today(), key="add_return_date", label_visibility="collapsed")

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)
    st.text_area("📝 Note", key="add_note", height=80)

    col1, col2 = st.columns(2)
    save_clicked   = col1.button("💾 Save",   key="add_save_btn",   use_container_width=True, type="primary")
    cancel_clicked = col2.button("❌ Cancel", key="add_cancel_btn", use_container_width=True)

    if cancel_clicked:
        st.session_state.add_errors    = {}
        st.session_state.active_dialog = None
        for key in ["add_brand_value", "add_model_value", "add_serial_value", "add_warranty_value", "add_status_value", "add_received_value"]:
            st.session_state.pop(key, None)
        for k in [k for k in st.session_state if k.startswith("add_")]: st.session_state.pop(k, None)
        st.rerun()

    if save_clicked:
        final_brand    = st.session_state.get("add_brand_value", "") or st.session_state.get("add_brand", "")
        final_model    = st.session_state.get("add_model_value", "") or st.session_state.get("add_model", "")
        final_serial   = st.session_state.get("add_serial_value", "") or st.session_state.get("add_serial", "")
        final_warranty = st.session_state.get("add_warranty_value", "") or st.session_state.get("add_warranty", "")
        final_status   = st.session_state.get("add_status_value", "") or st.session_state.get("add_status", "")
        final_received = st.session_state.get("add_received_value", "") or st.session_state.get("add_received", "")

        errors = validate_inventory({"brand": final_brand, "model": final_model, "serial": final_serial})
        st.session_state.add_errors = errors
        if errors: st.rerun()

        issue_date  = st.session_state.get("add_issue_date", None) if st.session_state.get("add_issue_type") == "Set Date" else None
        return_date = st.session_state.get("add_return_date", None) if st.session_state.get("add_return_type") == "Set Date" else None

        insert_inventory((final_brand or "", final_model or "", final_serial or "", st.session_state.get("add_category", "") or "",
                          final_warranty or "", st.session_state.get("add_qty", 1), final_status or "", st.session_state.get("add_handover", "") or "",
                          issue_date, final_received or "", return_date, st.session_state.get("add_note", "") or "", st.session_state.get("add_status2", "") or ""))

        fetch_distinct.clear()
        st.session_state.add_errors    = {}
        st.session_state.active_dialog = None
        for key in ["add_brand_value", "add_model_value", "add_serial_value", "add_warranty_value", "add_status_value", "add_received_value"]:
            st.session_state.pop(key, None)
        for k in [k for k in st.session_state if k.startswith("add_")]: st.session_state.pop(k, None)

        st.success("#### ✅ Saved Successfully!")
        time.sleep(0.4)
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
# EDIT INVENTORY DIALOG
# ═══════════════════════════════════════════════════════════════════
@st.dialog("✏️ Edit Inventory", width="large")
def edit_inventory_dialog():
    row = st.session_state.edit_row_data
    with st.form("edit_form"):
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        with r1c1: brand = st.text_input("Brand", value=row["brand"] or "")
        with r1c2: category = st.text_input("Category", value=row["item_category"] or "")
        with r1c3: model = st.text_input("Model", value=row["model"] or "")
        with r1c4: serial = st.text_input("Serial No.", value=row["serial_no"] or "")
        
        st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)
        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        with r2c1: qty = st.number_input("Quantity", value=int(row["quantity"]) if row["quantity"] is not None else 1, min_value=1)
        with r2c2: warranty = st.text_input("Warranty Status", value=row["warranty_status"] or "")
        with r2c3: status = st.text_input("Status", value=row["status"] or "")
        with r2c4: status_2 = st.text_input("Status-2", value=row.get("status_2") or "")
        
        st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)
        r3c1, r3c2 = st.columns(2)
        with r3c1: handover = st.text_input("Handover To", value=row.get("hand_over_to") or "")
        with r3c2: received = st.text_input("Received From", value=row.get("received_from") or "")
        
        st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)
        r4c1, r4c2 = st.columns(2)
        with r4c1:
            issue_type = st.radio("📅 Issue Date", ["Set Date", "NA"], horizontal=True, index=0 if row["issue_date"] else 1, key=f"is_{row['id']}")
            issue_date = st.date_input("Issue Date", value=safe_date(row["issue_date"]), key=f"is_d_{row['id']}", label_visibility="collapsed")
            issue_final = issue_date if issue_type == "Set Date" else None
        with r4c2:
            return_type = st.radio("📅 Return Date", ["Set Date", "NA"], horizontal=True, index=0 if row["return_date"] else 1, key=f"ret_{row['id']}")
            return_date = st.date_input("Return Date", value=safe_date(row["return_date"]), key=f"ret_d_{row['id']}", label_visibility="collapsed")
            return_final = return_date if return_type == "Set Date" else None

        st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)
        note = st.text_area("📝 Note", value=row.get("note") or "", height=80)
        c1, c2 = st.columns(2)
        save   = c1.form_submit_button("💾 Save",   use_container_width=True)
        cancel = c2.form_submit_button("❌ Cancel", use_container_width=True)

    if save:
        update_inventory((brand, model, serial, category, warranty, qty, status, handover, issue_final, received, return_final, note, status_2, row["id"]))
        st.session_state.edit_row_data  = None
        st.session_state.active_dialog  = None
        st.success("#### ✅ Updated Successfully!")
        time.sleep(0.4)
        st.rerun()

    if cancel:
        st.session_state.edit_row_data  = None
        st.session_state.active_dialog  = None
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
# CONFIRM DELETE DIALOG
# ═══════════════════════════════════════════════════════════════════
@st.dialog("🗑️ Confirm Delete")
def confirm_delete_dialog():
    item_id    = st.session_state.delete_id
    item_label = st.session_state.delete_label
    st.warning("Are you sure you want to delete this item?")
    st.markdown(f"**Item:** {item_label}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Yes, Delete", type="primary", use_container_width=True):
            delete_inventory(item_id)
            st.session_state.delete_id     = None
            st.session_state.delete_label  = ""
            st.session_state.active_dialog = None
            st.info("#### 🗑️ Deleted Successfully!")
            time.sleep(0.4)
            st.rerun()
    with c2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.delete_id     = None
            st.session_state.delete_label  = ""
            st.session_state.active_dialog = None
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# LOAD MAIN INVENTORY DATA
# ═══════════════════════════════════════════════════════════════════
df = fetch_inventory()
if not df.empty:
    df.columns = df.columns.str.strip().str.lower()

# ═══════════════════════════════════════════════════════════════════
# TOP LAYOUT ACTIONS ROW (Added Logout to the right of Download Excel)
# ═══════════════════════════════════════════════════════════════════
title_col, add_col, pdf_col, excel_col, logout_col = st.columns(
    [5.0, 1.1, 1.1, 1.1, 0.9], vertical_alignment="center"
)

with title_col:
    st.badge("**:material/inventory: Overall Inventory Status**", color="green")

with add_col:
    if st.button("Add Inventory", icon=":material/add_box:", key="add_inv_btn", use_container_width=True):
        st.session_state.active_dialog = "add"

with pdf_col:
    pdf_bytes = generate_inventory_pdf(df)
    st.download_button(
        label=":material/download: Download PDF", data=pdf_bytes,
        file_name=f"inventory-report_{date.today().strftime('%d-%m-%Y')}.pdf",
        mime="application/pdf", use_container_width=True, key="pdf_btn",
    )

with excel_col:
    excel_bytes = generate_inventory_excel(df)
    st.download_button(
        label=":material/description: Download Excel", data=excel_bytes,
        file_name=f"inventory-report_{date.today().strftime('%d-%m-%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True, key="excel_btn",
    )

with logout_col:
    if st.button("Log Out", icon=":material/logout:", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.pop("current_user", None)
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
# METRICS PANEL
# ═══════════════════════════════════════════════════════════════════
total     = len(df)
Issued    = len(df[df["status"].str.lower().isin(["issued","given", "in use"])]) if not df.empty else 0
Available = len(df[df["status"].str.lower().isin(["info-inventory", "inventory", "available","in inventory","in stock"])]) if not df.empty else 0
Damaged   = len(df[df["status"].str.lower().isin(["damaged", "broken", "maintenance"])]) if not df.empty else 0

with st.container(key="metrics_row"):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Row Items", total)
    c2.metric("Issued / Active", Issued)
    c3.metric("Available Stock", Available)
    c4.metric("Damaged / Repair", Damaged)

# ═══════════════════════════════════════════════════════════════════
# LIVE FILTERING SEARCH ENGINE
# ═══════════════════════════════════════════════════════════════════
if st.session_state.get("do_clear_search"):
    st.session_state.search_box      = ""
    st.session_state.do_clear_search = False
    st.rerun()

COL_WIDTHS        = [0.7, 0.8, 1.2, 1.0, 0.9, 0.9, 1.3, 1.2, 1.3, 1.1, 1.5, 1.3, 1.6, 1.2, 0.6, 0.6]
SEARCH_ROW_WIDTHS = [sum(COL_WIDTHS[:14]), sum(COL_WIDTHS[14:])]

search_col, refresh_col = st.columns(SEARCH_ROW_WIDTHS, vertical_alignment="bottom", gap="small")
with search_col:
    search2 = st.text_input("Search Inventory", placeholder="Search...", icon=":material/search:", label_visibility="collapsed", key="search_box")
with refresh_col:
    if st.button("Refresh", icon=":material/refresh:", key="refresh_btn", use_container_width=True):
        st.session_state.do_clear_search = True
        st.rerun()

list_df = df.copy().fillna("")
if search2 and search2.strip():
    mask = list_df.astype(str).apply(lambda col: col.str.contains(search2, case=False, na=False, regex=False)).any(axis=1)
    list_df = list_df[mask]

list_df = list_df.reset_index(drop=True)
list_df["s_no"] = list_df.index + 1

# ═══════════════════════════════════════════════════════════════════
# INVENTORY MAIN DATAGRID (HEADER & CORES)
# ═══════════════════════════════════════════════════════════════════
with st.container(key="header_row"):
    h0,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,h13,h14,h15 = st.columns(COL_WIDTHS, gap="small")
    h0.badge("S.No");        h1.badge("Brand");          h2.badge("Model")
    h3.badge("Serial No.");  h4.badge("Category");       h5.badge("Quantity")
    h6.badge("Warranty");    h7.badge("Status");         h8.badge("Handover To")
    h9.badge("Issue Date");  h10.badge("Received From"); h11.badge("Return Date")
    h12.badge("Note");       h13.badge("Status-2");      h14.badge("Edit"); h15.badge("Del.")

def small(val):            return f'<p style="font-size:12px;margin:0">{val}</p>'
def safe_val(val):         return "—" if val is None or (isinstance(val, float) and pd.isna(val)) or str(val).strip() == "" else val
def safe_date_str(val):    return "—" if val is None or str(val).strip() in ("", "None", "NaT", "NAN", "NaN") else str(val)

for _, row in list_df.iterrows():
    uid = str(row["id"])
    with st.container(key=f"row_{uid}"):
        c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15 = st.columns(COL_WIDTHS, gap="small")
        c0.markdown( small(safe_val(row["s_no"])),               unsafe_allow_html=True)
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

        if c14.button("✏️", key=f"edit_{uid}"):
            st.session_state.edit_row_data  = row.to_dict()
            st.session_state.active_dialog  = "edit"
            st.rerun()
        if c15.button(":material/delete:", key=f"del_{uid}"):
            b, m, s = safe_val(row["brand"]), safe_val(row["model"]), safe_val(row["serial_no"])
            st.session_state.delete_id     = row["id"]
            st.session_state.delete_label  = f"{b} — {m} (S/No: {s})"
            st.session_state.active_dialog = "delete"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# DIALOG ROUTING DISPATCHER
# ═══════════════════════════════════════════════════════════════════
if st.session_state.active_dialog == "add":       add_inventory_dialog()
elif st.session_state.active_dialog == "edit":     edit_inventory_dialog()
elif st.session_state.active_dialog == "delete":   confirm_delete_dialog()

st.divider()
st.caption("Inventory Management System • Dashboard")