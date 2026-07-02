import streamlit as st
import pandas as pd
from datetime import date, datetime

from db_connection import get_connection
from streamlit_searchbox import st_searchbox

st.set_page_config(page_title="Inventory", layout="wide")

st.markdown("""
<style>
html { zoom: 72%; }
.block-container { padding-top: 0rem; padding-bottom: 0rem; }
header[data-testid="stHeader"] { display: none; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ======================
# SESSION STATE
# ======================
for k in ["edit_row", "delete_id", "delete_label"]:
    if k not in st.session_state:
        st.session_state[k] = None


# ======================
# CONFIG
# ======================
COL_WIDTHS = [0.5, 1.2, 1.2, 1.5, 1.2, 0.8, 1, 1, 1.2, 1.2, 1.2, 1.2, 1.5, 1, 0.6, 0.6]


# ======================
# HELPERS
# ======================
def safe_val(val):
    if val is None or str(val).strip() == "":
        return "—"
    if isinstance(val, float) and pd.isna(val):
        return "—"
    return str(val)


def safe_date_str(val):
    if val is None or str(val).strip() in ("", "None", "NaT"):
        return "—"
    return str(val)


# ======================
# DB
# ======================
def fetch_inventory():
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
    conn.close()

    cols = [
        "id","brand","model","serial_no","item_category","quantity",
        "warranty_status","status","hand_over_to","issue_date",
        "received_from","return_date","note","status_2"
    ]

    return pd.DataFrame(rows, columns=cols)


def search_inventory_items(searchterm: str):
    conn = get_connection()
    cur = conn.cursor()

    if not searchterm:
        cur.execute("""
            SELECT brand || ' - ' || model || ' (SN: ' || serial_no || ')'
            FROM inventory
            ORDER BY id DESC
            LIMIT 10
        """)
    else:
        cur.execute("""
            SELECT brand || ' - ' || model || ' (SN: ' || serial_no || ')'
            FROM inventory
            WHERE brand LIKE ?
               OR model LIKE ?
               OR serial_no LIKE ?
            LIMIT 10
        """, (f"%{searchterm}%", f"%{searchterm}%", f"%{searchterm}%"))

    results = [r[0] for r in cur.fetchall()]
    conn.close()
    return results


# ======================
# LOAD DATA
# ======================
df = fetch_inventory()

if not df.empty:
    df.columns = df.columns.str.lower()


# ======================
# SEARCHBOX
# ======================
search_selected = st_searchbox(
    search_inventory_items,
    placeholder="Search inventory (brand / model / serial)...",
    key="inventory_search"
)

free_text = st.session_state.get("inventory_search", "")
search_value = search_selected or free_text


# ======================
# FILTER
# ======================
list_df = df.copy().fillna("")

if search_value and search_value.strip():
    mask = list_df.astype(str).apply(
        lambda col: col.str.contains(search_value, case=False, na=False, regex=False)
    ).any(axis=1)

    list_df = list_df[mask]

list_df = list_df.reset_index(drop=True)
list_df["s_no"] = list_df.index + 1


# ======================
# HEADER
# ======================
headers = [
    "S.No", "Brand", "Model", "Serial", "Category", "Qty",
    "Warranty", "Status", "Handover", "Issue Date",
    "Received", "Return Date", "Note", "Status-2", "Edit", "Del"
]

with st.container():
    cols = st.columns(COL_WIDTHS)

    for i, h in enumerate(headers):
        cols[i].markdown(f"**{h}**")


# ======================
# ROWS
# ======================
def cell(col, value):
    col.markdown(f"<p style='font-size:12px;margin:0'>{safe_val(value)}</p>", unsafe_allow_html=True)


for _, row in list_df.iterrows():
    uid = str(row["id"])

    c = st.columns(COL_WIDTHS)

    cell(c[0], row["s_no"])
    cell(c[1], row["brand"])
    cell(c[2], row["model"])
    cell(c[3], row["serial_no"])
    cell(c[4], row["item_category"])
    cell(c[5], row["quantity"])
    cell(c[6], row["warranty_status"])
    cell(c[7], row["status"])
    cell(c[8], row.get("hand_over_to"))
    cell(c[9], row["issue_date"])
    cell(c[10], row.get("received_from"))
    cell(c[11], row["return_date"])
    cell(c[12], row.get("note"))
    cell(c[13], row.get("status_2"))

    if c[14].button("✏️", key=f"edit_{uid}"):
        st.session_state.edit_row = row.to_dict()
        st.info("Edit clicked (dialog not implemented)")

    if c[15].button("🗑️", key=f"del_{uid}"):
        st.session_state.delete_id = row["id"]
        st.session_state.delete_label = f'{row["brand"]} - {row["model"]}'
        st.warning("Delete clicked (dialog not implemented)")


st.divider()
st.caption("Inventory Management System • Dashboard")