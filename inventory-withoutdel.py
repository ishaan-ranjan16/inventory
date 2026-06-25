import streamlit as st
import pandas as pd
from datetime import date
import io
from db_connection import get_connection

from datetime import datetime

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


st.set_page_config(page_title="Inventory", layout="wide")

# ==========================
# GLOBAL STYLE
# ==========================
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

# ==========================
# SESSION STATE
# ==========================
if "edit_row" not in st.session_state:
    st.session_state.edit_row = None

def safe_date(val):
    if val is None or (isinstance(val, str) and val.strip() == ""):
        return date.today()
    if isinstance(val, str):
        try:
            return datetime.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            return date.today()
    return val if pd.notna(val) else date.today()

# ==========================
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

        # sqlite3.Row objects → list of plain tuples for DataFrame
        return pd.DataFrame([tuple(r) for r in rows], columns=columns)

    except Exception as e:
        print(f"CRITICAL DATABASE ERROR: {e}")
        st.error("⚠️ Downtime Alert: Unable to connect to the inventory database. Please try again later.")
        return pd.DataFrame(columns=columns)


def insert_inventory(data):
    conn = get_connection()
    cur = conn.cursor()

    clean_data = list(data)
    if clean_data[8]:   # issue_date
        clean_data[8] = clean_data[8].strftime('%Y-%m-%d')
    if clean_data[10]:  # return_date
        clean_data[10] = clean_data[10].strftime('%Y-%m-%d')

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
    cur = conn.cursor()

    clean_values = list(values)
    if clean_values[8]:   # issue_final
        clean_values[8] = clean_values[8].strftime('%Y-%m-%d')
    if clean_values[10]:  # return_final
        clean_values[10] = clean_values[10].strftime('%Y-%m-%d')

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
        # WHERE serial_no=?


    conn.commit()
    cur.close()
    conn.close()


# def delete_inventory(serial_no):
#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute("DELETE FROM inventory WHERE serial_no=?", (serial_no,))
#     conn.commit()
#     cur.close()
#     conn.close()
def delete_inventory(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventory WHERE id=?", (id,))
    conn.commit()
    cur.close()
    conn.close()

# ==========================
# EXCEL EXPORT
# ==========================
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

# ==========================
# PDF EXPORT
# ==========================
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

# ======================
# ADD INVENTORY
# ======================
@st.dialog("📝 Add Inventory")
def add_inventory_dialog():
    with st.form("add_form", clear_on_submit=True):
        brand       = st.text_input("Brand")
        category    = st.text_input("Category")
        model       = st.text_input("Model")
        serial_no   = st.text_input("Serial Number")
        qty         = st.number_input("Quantity", value=1, min_value=1)
        warranty    = st.text_input("Warranty Status")
        status      = st.text_input("Status")
        handover    = st.text_input("Handover To")
        received_from = st.text_input("Received From")

        issue_type = st.radio("Issue Date Type", ["Date", "NA"], horizontal=True, key="add_issue_type")
        issue_date = (
            st.date_input("Issue Date", value=date.today(), key="add_issue_date")
            if issue_type == "Date" else None
        )

        return_type = st.radio("Return Date Type", ["Date", "NA"], horizontal=True, key="add_return_type")
        return_date = (
            st.date_input("Return Date", value=date.today(), key="add_return_date")
            if return_type == "Date" else None
        )

        note     = st.text_area("📝 Note")
        status_2 = st.text_input("Status-2")

        submit = st.form_submit_button(":heavy_plus_sign: Add Item")

        if submit:
            insert_inventory((
                brand, model, serial_no, category,
                warranty, qty, status,
                handover, issue_date,
                received_from, return_date,
                note, status_2
            ))
            st.success("Added Successfully")
            st.rerun()

# ==========================
# EDIT INVENTORY
# ==========================
@st.dialog("✏️ Edit Inventory")
def edit_inventory_dialog():
    row = st.session_state.edit_row

    with st.form("edit_form"):
        brand    = st.text_input("Brand",    value=row["brand"])
        category = st.text_input("Category", value=row["item_category"])
        model    = st.text_input("Model",    value=row["model"])
        serial   = st.text_input("Serial No", value=row["serial_no"])

        qty = st.number_input(
            "Quantity",
            value=int(row["quantity"]) if row["quantity"] is not None else 1,
            min_value=1
        )

        warranty = st.text_input("Warranty Status", value=row["warranty_status"] or "")
        status   = st.text_input("Status",          value=row["status"] or "")
        handover = st.text_input("Handover To",     value=row.get("hand_over_to") or "")
        received = st.text_input("Received From",   value=row.get("received_from") or "")

        issue_type = st.radio(
            "Issue Date Type", ["Date", "NA"], horizontal=True,
            index=0 if row["issue_date"] else 1,
            key=f"issue_{row['id']}"
        )
        issue_date = st.date_input(
            "Issue Date",
            value=safe_date(row["issue_date"]),
            key=f"issue_date_{row['id']}"
        )
        issue_final = issue_date if issue_type == "Date" else None

        return_type = st.radio(
            "Return Date Type", ["Date", "NA"], horizontal=True,
            index=0 if row["return_date"] else 1,
            key=f"return_{row['id']}"
        )
        return_date = st.date_input(
            "Return Date",
            value=safe_date(row["return_date"]),
            key=f"return_date_{row['id']}"
        )
        return_final = return_date if return_type == "Date" else None

        note     = st.text_area("📝 Note", value=row.get("note") or "")
        status_2 = st.text_input("Status-2", value=row.get("status_2") or "")

        c1, c2 = st.columns(2)
        save   = c1.form_submit_button("💾 Save")
        cancel = c2.form_submit_button("❌ Cancel")

    if save:
        payload = (
            brand, model, serial, category,
            warranty, qty, status,
            handover, issue_final,
            received, return_final,
            note, status_2,
            row["id"]   
            # row["serial_no"]   # WHERE clause
        )
        update_inventory(payload)
        st.success("Updated Successfully")
        st.rerun()

    if cancel:
        st.rerun()

# ==========================
# LOAD DATA
# ==========================
def load_data():
    return fetch_inventory()

df = load_data()

if not df.empty:
    df.columns = df.columns.str.strip().str.lower()

# ==========================
# TOP HEADER ROW
# ==========================
title_col, add_col, pdf_col, excel_col = st.columns(
    [6, 1.1, 1.1, 1.1], vertical_alignment="center"
)

with title_col:
    st.badge("**:material/inventory: Overall Inventory Status**", color='green')

with add_col:
    if st.button("Add Inventory", icon=":material/add_box:", key="add_inv_btn", use_container_width=True):
        add_inventory_dialog()

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

# ==========================
# METRICS
# ==========================
total     = len(df)
Issued    = len(df[df["status"].str.lower().isin(["issued"])])
Available = len(df[df["status"].str.lower().isin(["in-inventory", "inventory"])])
Damaged   = len(df[df["status"].str.lower().isin(["damaged"])])


# total = len(df)

# Issued = (
#     (df["status"].notna()) &
#     (df["status-2"].fillna("").str.lower() == "issued")
# ).sum()

# Available = (
#     df["status"].fillna("").str.lower().isin(
#         ["in-inventory", "inventory"]
#     )
# ).sum()

# Damaged = (
#     df["status"].fillna("").str.lower() == "damaged"
# ).sum()

# Issued = len(df[df["status"].str.lower().isin(["Issued","issued","ISSUED"])]) 
#  # Use .str.lower() to make the comparison case-insensitive

# Available = len(df[df["status"].str.lower().isin(["In-Inventory","in-inventory","inventory","Inventory", "IN-INVENTORY"])])  

# Damaged = len(df[df["status"].str.lower().isin(["Damaged","damaged","DAMAGED"])])  

with st.container(key="metrics_row"):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total",        total)
    c2.metric("Issued",       Issued)
    c3.metric("In-Inventory", Available)
    c4.metric("Damaged",      Damaged)

# ==========================
# SEARCH + REFRESH
# ==========================
if st.session_state.get("do_clear_search"):
    st.session_state.search_box = ""
    st.session_state.do_clear_search = False

COL_WIDTHS = [0.7, 0.8, 1.2, 1.0, 0.9, 0.9, 1.3, 1.2, 1.3, 1.1, 1.5, 1.3, 1.6, 1.2, 0.6, 0.6]
SEARCH_ROW_WIDTHS = [sum(COL_WIDTHS[:14]), sum(COL_WIDTHS[14:])]

search_col, refresh_col = st.columns(SEARCH_ROW_WIDTHS, vertical_alignment="bottom", gap="small")

with search_col:
    search2 = st.text_input(
        "Search Inventory List",
        placeholder="Search...",
        icon=":material/search:",
        label_visibility="collapsed",
        key="search_box"
    )

with refresh_col:
    if st.button(":material/refresh:", key="refresh_btn", use_container_width=True):
        st.session_state.do_clear_search = True
        st.rerun()

list_df = df.copy()

if search2:
    list_df = list_df[
        list_df.apply(
            lambda r: r.astype(str).str.contains(search2, case=False, na=False).any(),
            axis=1
        )
    ]

list_df = list_df.reset_index(drop=True)
list_df["s_no"] = list_df.index + 1

# ==========================
# TABLE — HEADER
# ==========================
with st.container(key="header_row"):
    h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15 = st.columns(
        COL_WIDTHS, gap="small"
    )
    h0.badge("S.No");       h1.badge("Brand");        h2.badge("Model")
    h3.badge("Serial No."); h4.badge("Category");     h5.badge("Quantity")
    h6.badge("Warranty");   h7.badge("Status");       h8.badge("Handover To")
    h9.badge("Issue Date"); h10.badge("Received From"); h11.badge("Return Date")
    h12.badge("Note");      h13.badge("Status-2");    h14.badge("Edit");  h15.badge("Del.")

# ==========================
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
    """Returns a display string for a date column (stored as TEXT in SQLite)."""
    if val is None or str(val).strip() in ("", "None", "NaT"):
        return "—"
    return str(val)

for _, row in list_df.iterrows():
    uid = str(row["id"])

    with st.container(key=f"row_{uid}"):
        c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15 = st.columns(
            COL_WIDTHS, gap="small"
        )

        c0.markdown(small(safe_val(row["s_no"])),           unsafe_allow_html=True)
        c1.markdown(small(safe_val(row["brand"])),           unsafe_allow_html=True)
        c2.markdown(small(safe_val(row["model"])),           unsafe_allow_html=True)
        c3.markdown(small(safe_val(row["serial_no"])),       unsafe_allow_html=True)
        c4.markdown(small(safe_val(row["item_category"])),   unsafe_allow_html=True)
        c5.markdown(small(safe_val(row["quantity"])),        unsafe_allow_html=True)
        c6.markdown(small(safe_val(row["warranty_status"])), unsafe_allow_html=True)
        c7.markdown(small(safe_val(row["status"])),          unsafe_allow_html=True)
        c8.markdown(small(safe_val(row.get("hand_over_to"))), unsafe_allow_html=True)
        c9.markdown(small(safe_date_str(row["issue_date"])), unsafe_allow_html=True)
        c10.markdown(small(safe_val(row.get("received_from"))), unsafe_allow_html=True)
        c11.markdown(small(safe_date_str(row["return_date"])), unsafe_allow_html=True)
        c12.markdown(small(safe_val(row.get("note"))),       unsafe_allow_html=True)
        c13.markdown(small(safe_val(row.get("status_2"))),   unsafe_allow_html=True)

        if c14.button("✏️", key=f"edit_{uid}"):
            st.session_state.edit_row = row.to_dict()
            edit_inventory_dialog()

        if c15.button(":material/delete:", key=f"del_{uid}"):
            delete_inventory(row["id"])
            st.warning("Deleted Successfully")
            st.rerun()

st.divider()
st.caption("Inventory Management System • Dashboard")