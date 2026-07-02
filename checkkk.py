import streamlit as st
import pandas as pd
from datetime import date, datetime
import io
from db_connection import get_connection
import time
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Inventory", layout="wide")

st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
    <style>
        html { zoom: 72%; }

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
        .st-key-excel_btn button {
            padding: 4px 10px !important;
            font-size: 13px !important;
            white-space: nowrap !important;
            height: auto !important;
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
    </style>
""", unsafe_allow_html=True)

# SESSION STATE
# ==========================
if "edit_row" not in st.session_state:
    st.session_state.edit_row = None

if "delete_id" not in st.session_state:
    st.session_state.delete_id = None

if "delete_label" not in st.session_state:
    st.session_state.delete_label = ""

if "add_errors" not in st.session_state:
    st.session_state.add_errors = {}

if "show_add_dialog" not in st.session_state:
    st.session_state.show_add_dialog = False

# ==================
def safe_date(val):
    """For pre-filling date_input widgets — always returns a date object."""
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
    """
    Convert date / datetime / ISO-string / None → 'YYYY-MM-DD' string or None.
    Handles the case where Streamlit session_state delivers a stale string
    instead of a date object when a widget was never rendered this run.
    """
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.strftime('%d-%m-%Y')
    if isinstance(val, date):
        return val.strftime('%d-%m-%Y')
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        try:
            datetime.strptime(s, '%d-%m-%Y')   # validate format
            return s                             # already a clean string
        except ValueError:
            return None
    return None

# DATABASE FUNCTIONS
# ==========================
def fetch_inventory():
    columns = [
        "id", "brand", "model", "serial_no", "item_category", "quantity",
        "warranty_status", "status", "hand_over_to", "issue_date",
        "received_from", "return_date", "note", "status_2"
    ]

    try:
        conn = get_connection()
        cur = conn.cursor()
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
        st.error("⚠️ Downtime Alert: Unable to connect to the inventory database. Please try again later.")
        return pd.DataFrame(columns=columns)

def insert_inventory(data):
    """
    data tuple order:
      brand, model, serial_no, item_category, warranty_status, quantity,
      status, hand_over_to, issue_date, received_from, return_date, note, status_2
    """
    conn = get_connection()
    cur  = conn.cursor()

    clean_data = list(data)
    clean_data[8]  = _safe_date_str(clean_data[8])   # issue_date  (index 8)
    clean_data[10] = _safe_date_str(clean_data[10])  # return_date (index 10)

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
    """
    values tuple order:
      brand, model, serial_no, item_category, warranty_status, quantity,
      status, hand_over_to, issue_date, received_from, return_date, note,
      status_2, id
    """
    conn = get_connection()
    cur  = conn.cursor()

    clean_values = list(values)
    clean_values[8]  = _safe_date_str(clean_values[8])   # issue_date
    clean_values[10] = _safe_date_str(clean_values[10])  # return_date

    cur.execute("""
        UPDATE inventory
        SET
            brand=?,
            model=?,
            serial_no=?,
            item_category=?,
            warranty_status=?,
            quantity=?,
            status=?,
            hand_over_to=?,
            issue_date=?,
            received_from=?,
            return_date=?,
            note=?,
            status_2=?
        WHERE id=?
    """, tuple(clean_values))

    conn.commit()
    cur.close()
    conn.close()

def delete_inventory(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventory WHERE id=?", (id,))
    conn.commit()
    cur.close()
    conn.close()

# EXCEL EXPORT
# =================
def generate_inventory_excel(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()

    export_df = data.reset_index(drop=True).copy()

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

    export_df = export_df[columns]
    export_df.insert(0, "s_no", export_df.index + 1)
    export_df.columns = headers

    export_df = export_df.fillna("—")
    export_df = export_df.replace("", "—")

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Inventory")

        worksheet = writer.sheets["Inventory"]
        for i, col in enumerate(export_df.columns):
            max_len = max(
                export_df[col].astype(str).map(len).max() if not export_df.empty else 0,
                len(str(col))
            ) + 2
            col_letter = chr(65 + i) if i < 26 else "A" + chr(65 + i - 26)
            worksheet.column_dimensions[col_letter].width = max_len

    buffer.seek(0)
    return buffer.getvalue()
# PDF EXPORT
# ==================
def generate_inventory_pdf(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10 * mm, rightMargin=10 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Inventory Report", styles["Title"]))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    data = data.reset_index(drop=True)

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
            line.append(str(val) if val is not None and val != "" and (not isinstance(val, float) or not pd.isna(val)) else "—")
        table_data.append(line)

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F7")]),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================
# AUTOCOMPLETE HELPERS (SQLite-backed)
# ==========================

def get_suggestions(column, limit=8):
    """
    Fetch DISTINCT values from SQLite for autocomplete suggestions.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(f"""
            SELECT DISTINCT {column}
            FROM inventory
            WHERE {column} IS NOT NULL
              AND TRIM({column}) != ''
            ORDER BY {column} ASC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        return [r[0] for r in rows if r[0]]
    finally:
        cur.close()
        conn.close()


def filter_suggestions(options, query):
    """
    Simple in-memory filter for live typing.
    """
    if not query:
        return options
    q = query.lower().strip()
    return [o for o in options if q in str(o).lower()]


def autocomplete_input(label, key, db_column):
    """
    Custom autocomplete widget:
    - free typing
    - shows clickable suggestions
    - stores final value in session_state[key]
    """

    # initialize state
    if f"{key}_value" not in st.session_state:
        st.session_state[f"{key}_value"] = ""

    if f"{key}_suggestions" not in st.session_state:
        st.session_state[f"{key}_suggestions"] = []

    # TEXT INPUT (free typing)
    typed = st.text_input(label, key=f"{key}_input")

    # update stored value
    st.session_state[f"{key}_value"] = typed

    # fetch + filter suggestions
    all_options = get_suggestions(db_column)
    filtered = filter_suggestions(all_options, typed)

    st.session_state[f"{key}_suggestions"] = filtered[:6]

    # SUGGESTION UI
    if filtered and typed:
        st.caption("Suggestions:")

        cols = st.columns(len(filtered[:6]))

        for i, option in enumerate(filtered[:6]):
            with cols[i]:
                if st.button(option, key=f"{key}_sug_{i}"):
                    st.session_state[f"{key}_value"] = option
                    st.session_state[f"{key}_input"] = option
                    st.rerun()

    return st.session_state[f"{key}_value"]

# DIALOG — SCROLLBAR STYLE
# ==========================
st.markdown("""
    <style>
    div[data-testid="stDialog"] *::-webkit-scrollbar { width: 10px; }
    div[data-testid="stDialog"] *::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    div[data-testid="stDialog"] *::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #4CAF50, #2196F3); border-radius: 10px; }
    div[data-testid="stDialog"] *::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #45a049, #1976D2); }
    div[data-testid="stDialog"] { scrollbar-width: thin; scrollbar-color: #2196F3 #f1f1f1; }
    </style>
""", unsafe_allow_html=True)

# VALIDATION
# ==================
def validate_inventory(data):
    errors = {}
    if not (data["brand"] or "").strip():
        errors["brand"] = "Brand is required."
    if not (data["model"] or "").strip():
        errors["model"] = "Model is required."
    if not (data["serial"] or "").strip():
        errors["serial"] = "Serial No. is required."
    return errors


@st.dialog("📝 Add Inventory", width="large")
def add_inventory_dialog():
    errors = st.session_state.add_errors or {}

    if errors:
        st.markdown(
            ":orange-badge[⚠️ Please enter the highlighted fields below.]"
            )

    with st.form("add_form"):
        # — Row 1: Brand | Category | Model | Serial No —
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        with r1c1:
            st.markdown("Brand <span style='color:red'>*</span>", unsafe_allow_html=True)
            # st.text_input("Enter Brand", label_visibility="collapsed", key="add_brand")
            # BRAND (autocomplete)
            add_brand = autocomplete_input(
                "Brand",
                "add_brand",
                "brand"
                )
            
            if "brand" in errors:
                st.markdown(
                    f"<p style='color:red; font-size:13px;'>{errors['brand']}</p>",
                    unsafe_allow_html=True
                    )
                # st.error(errors["brand"])
        with r1c2:
            st.text_input("Category", value="Laptop", key="add_category")
        with r1c3:
            st.markdown("Model <span style='color:red'>*</span>", unsafe_allow_html=True)
            # st.text_input("Enter Model", label_visibility="collapsed", key="add_model")
            # MODEL (autocomplete)
            add_model = autocomplete_input(
                "Model",
                "add_model",
                "model"
                )
            
            if "model" in errors:
                st.markdown(
                    f"<p style='color:red; font-size:13px;'>{errors['model']}</p>",
                    unsafe_allow_html=True
                    )

        with r1c4:
            st.markdown("Serial No. <span style='color:red'>*</span>", unsafe_allow_html=True)
            # st.text_input("Enter Serial Number", label_visibility="collapsed", key="add_serial")
            add_serial = autocomplete_input(
                "Serial No",
                "add_serial",
                "serial_no"
                )
            
            if "serial" in errors:
                st.markdown(
                    f"<p style='color:red; font-size:13px;'>{errors['serial']}</p>",
                    unsafe_allow_html=True
                    )
        st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

        # — Row 2: Qty | Warranty | Status | Status-2 —
        r2c1, r2c2, r2c3, r2c4 = st.columns(4)

        with r2c1:
            st.number_input("Quantity", min_value=1, value=1, key="add_qty")
        with r2c2:
            # st.text_input("Warranty Status", key="add_warranty")
            # WARRANTY STATUS (autocomplete)
            add_warranty = autocomplete_input(
                "Warranty Status",
                "add_warranty",
                "warranty_status"
                )
            
        with r2c3:
            # st.text_input("Status", key="add_status")
            # STATUS (autocomplete)
            add_status = autocomplete_input(
                "Status",
                "add_status",
                "status"
                )

        with r2c4:
            st.text_input("Status-2", key="add_status2")

        st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

        # — Row 3: Handover To | Received From —
        r3c1, r3c2 = st.columns(2)
        with r3c1:
            st.text_input("Handover To", key="add_handover")
        with r3c2:
            # st.text_input("Received From", key="add_received")
            # RECEIVED FROM (autocomplete)
            add_received = autocomplete_input(
                "Received From",
                "add_received",
                "received_from"
                )


        st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)
        # — Row 4: Issue Date | Return Date —
        r4c1, r4c2 = st.columns(2)
        with r4c1:
            issue_type = st.radio(
                "📅 Issue Date", ["Set Date", "NA (not issued/in-inventory/available)"],
                horizontal=True, key="add_issue_type"
            )
            if issue_type == "Set Date":
                st.date_input(
                    "Issue Date", value=date.today(),
                    key="add_issue_date", label_visibility="collapsed"
                )
        with r4c2:
            return_type = st.radio(
                "📅 Return Date", ["Set Date", "NA (in-inventory/not returned/in-use)"],
                horizontal=True, key="add_return_type"
            )
            if return_type == "Set Date":
                st.date_input(
                    "Return Date", value=date.today(),
                    key="add_return_date", label_visibility="collapsed"
                )
        st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)
        st.text_area("📝 Note", key="add_note", height=80)
        # — Buttons —
        col1, col2 = st.columns(2)
        submit = col1.form_submit_button("💾 Save", use_container_width=True)
        cancel = col2.form_submit_button("❌ Cancel",   use_container_width=True)

    if cancel:
        st.session_state.add_errors = {}
        st.session_state.show_add_dialog = False
        
        for k in list(st.session_state.keys()):
            if k.startswith("add_"):
                del st.session_state[k]
        st.rerun()

    if submit:
        data = {
            "brand":  st.session_state.get("add_brand",  ""),
            "model":  st.session_state.get("add_model",  ""),
            "serial": st.session_state.get("add_serial", ""),
        }

        errors = validate_inventory(data)
        st.session_state.add_errors = errors
    
        if errors:
            st.rerun()

        issue_type  = st.session_state.get("add_issue_type",  "NA")
        return_type = st.session_state.get("add_return_type", "NA")

        issue_date  = st.session_state.get("add_issue_date",  None) if issue_type  == "Set Date" else None
        return_date = st.session_state.get("add_return_date", None) if return_type == "Set Date" else None

        insert_inventory((
            st.session_state.get("add_brand_value", ""),
            st.session_state.get("add_model_value", ""),
            st.session_state.get("add_serial_value", ""),
            st.session_state.get("add_category", ""),
            st.session_state.get("add_warranty_value", ""),
            st.session_state.get("add_qty", 1),
            st.session_state.get("add_status_value", ""),
            st.session_state.get("add_handover", ""),
            issue_date,
            st.session_state.get("add_received_value", ""),
            return_date,
            st.session_state.get("add_note", ""),
            st.session_state.get("add_status2", ""),
            ))

        # insert_inventory((
        #     st.session_state.get("add_brand", ""),
        #     st.session_state.get("add_model", ""),
        #     st.session_state.get("add_serial", ""),
        #     st.session_state.get("add_category", ""),
        #     st.session_state.get("add_warranty", ""),
        #     st.session_state.get("add_qty", 1),
        #     st.session_state.get("add_status", ""),
        #     st.session_state.get("add_handover", ""),
        #     issue_date,
        #     st.session_state.get("add_received", ""),
        #     return_date,
        #     st.session_state.get("add_note", ""),
        #     st.session_state.get("add_status2", ""),
        # ))

        st.session_state.add_errors = {}
        st.session_state.show_add_dialog = False
        
        for k in list(st.session_state.keys()):
            if k.startswith("add_"):
                del st.session_state[k]
                
        st.success("#### ✅ Saved Successfully!")
        time.sleep(0.5)
        st.rerun()