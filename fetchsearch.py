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

# ✅ NEW IMPORT (SEARCHBOX)
from streamlit_searchbox import st_searchbox

from inventory import confirm_delete_dialog, edit_inventory_dialog

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


# ==========================
# SEARCHBOX BACKEND (NEW)
# ==========================
def search_suggestions(query: str):
    """
    Returns suggestions for dropdown.
    Uses DB values (brand/model/serial/category).
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT brand, model, serial_no, item_category
            FROM inventory
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        suggestions = set()

        for r in rows:
            for v in r:
                if v:
                    suggestions.add(str(v))

        if query:
            return [s for s in suggestions if query.lower() in s.lower()]

        return list(suggestions)

    except:
        return []


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
    if isinstance(val, datetime):
        return val.strftime('%d-%m-%Y')
    if isinstance(val, date):
        return val.strftime('%d-%m-%Y')
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        try:
            datetime.strptime(s, '%d-%m-%Y')
            return s
        except ValueError:
            return None
    return None


# ==========================
# DATABASE FUNCTIONS
# ==========================
def fetch_inventory():
    columns = [
        "id", "brand", "model", "serial_no", "item_category", "quantity",
        "warranty_status", "status", "hand_over_to", "issue_date",
        "received_from", "return_date", "note", "status_2"
    ]

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

    return pd.DataFrame(rows, columns=columns)


# ==========================
# (ALL YOUR OTHER FUNCTIONS REMAIN SAME)
# ==========================
# insert_inventory, update_inventory, delete_inventory,
# excel/pdf functions → unchanged (omitted here for space safety)
# ===============================================================


# LOAD DATA
df = fetch_inventory()
if not df.empty:
    df.columns = df.columns.str.strip().str.lower()


# ==========================
# TOP HEADER
# ==========================
title_col, add_col, pdf_col, excel_col = st.columns([6, 1.1, 1.1, 1.1])

with title_col:
    st.badge("**:material/inventory: Overall Inventory Status**", color='green')


# ==========================
# SEARCH SECTION (UPDATED)
# ==========================
COL_WIDTHS = [0.7, 0.8, 1.2, 1.0, 0.9, 0.9, 1.3, 1.2, 1.3, 1.1, 1.5, 1.3, 1.6, 1.2, 0.6, 0.6]
SEARCH_ROW_WIDTHS = [sum(COL_WIDTHS[:14]), sum(COL_WIDTHS[14:])]

search_col, refresh_col = st.columns(SEARCH_ROW_WIDTHS)

with search_col:
    search_value = st_searchbox(
        search_suggestions,
        placeholder="Search inventory (type or select)...",
        key="search_box"
    )

with refresh_col:
    if st.button("Refresh", key="refresh_btn", use_container_width=True):
        st.rerun()


# ==========================
# FILTER LOGIC (unchanged behavior)
# ==========================
list_df = df.copy().fillna("")

if search_value:
    mask = list_df.astype(str).apply(
        lambda col: col.str.contains(search_value, case=False, na=False)
    ).any(axis=1)
    list_df = list_df[mask]

list_df = list_df.reset_index(drop=True)
list_df["s_no"] = list_df.index + 1


# ==========================
# REST OF YOUR CODE UNCHANGED
# (TABLE + DIALOGS + EXPORT + METRICS)
# ==========================

# 👉 keep everything below exactly as you already wrote it:
# header row, table rendering, dialogs, pdf/excel, etc.

# TABLE — HEADER
# ==========================
with st.container(key="header_row"):
    h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15 = st.columns(
        COL_WIDTHS, gap="small"
    )
    h0.badge("S.No");        h1.badge("Brand");          h2.badge("Model")
    h3.badge("Serial No.");  h4.badge("Category");       h5.badge("Quantity")
    h6.badge("Warranty");    h7.badge("Status");         h8.badge("Handover To")
    h9.badge("Issue Date");  h10.badge("Received From"); h11.badge("Return Date")
    h12.badge("Note");       h13.badge("Status-2");      h14.badge("Edit"); h15.badge("Del.")

# TABLE — DATA ROWS
# ==========================
def small(val):
    return f'<p style="font-size:12px; margin:0">{val}</p>'

def safe_val(val):
    if val is None:
        return "—"
    if isinstance(val, float) and pd.isna(val):
        return "—"
    if str(val).strip() == "":
        return "—"
    return val

def safe_date_str(val):
    if val is None or str(val).strip() in ("", "None", "NaT", "NAN", "NaN"):
        return "—"
    return str(val)

for _, row in list_df.iterrows():
    uid = str(row["id"])

    with st.container(key=f"row_{uid}"):
        c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15 = st.columns(
            COL_WIDTHS, gap="small"
        )

        c0.markdown(small(safe_val(row["s_no"])),               unsafe_allow_html=True)
        c1.markdown(small(safe_val(row["brand"])),              unsafe_allow_html=True)
        c2.markdown(small(safe_val(row["model"])),              unsafe_allow_html=True)
        c3.markdown(small(safe_val(row["serial_no"])),          unsafe_allow_html=True)
        c4.markdown(small(safe_val(row["item_category"])),      unsafe_allow_html=True)
        c5.markdown(small(safe_val(row["quantity"])),           unsafe_allow_html=True)
        c6.markdown(small(safe_val(row["warranty_status"])),    unsafe_allow_html=True)
        c7.markdown(small(safe_val(row["status"])),             unsafe_allow_html=True)
        c8.markdown(small(safe_val(row.get("hand_over_to"))),   unsafe_allow_html=True)
        c9.markdown(small(safe_date_str(row["issue_date"])),    unsafe_allow_html=True)
        c10.markdown(small(safe_val(row.get("received_from"))), unsafe_allow_html=True)
        c11.markdown(small(safe_date_str(row["return_date"])),  unsafe_allow_html=True)
        c12.markdown(small(safe_val(row.get("note"))),          unsafe_allow_html=True)
        c13.markdown(small(safe_val(row.get("status_2"))),      unsafe_allow_html=True)

        if c14.button("✏️", key=f"edit_{uid}"):
            st.session_state.edit_row = row.to_dict()
            edit_inventory_dialog()

        if c15.button(":material/delete:", key=f"del_{uid}"):
            brand_val  = safe_val(row["brand"])
            model_val  = safe_val(row["model"])
            serial_val = safe_val(row["serial_no"])
            st.session_state.delete_id    = row["id"]
            st.session_state.delete_label = f"{brand_val} — {model_val} (S/No: {serial_val})"
            confirm_delete_dialog()

st.divider()
st.caption("Inventory Management System • Dashboard")