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
# GLOBAL STYLE — remove top padding / hide default header
# ==========================
st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
    <style>
        html {
            zoom: 79%;
        }

        /* Remove the default top padding above your content */
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            margin-top: 0rem;
            margin-bottom: -5rem;
        }

        /* Hide the Streamlit header bar entirely (hamburger menu, deploy button) */
        header[data-testid="stHeader"] {
            display: none;
        }

        /* Hide the colored decoration line under the header */
        [data-testid="stDecoration"] {
            display: none;
        }

        div[data-testid="stMetricValue"] {
            font-size: 15px;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 13px;
        }

        /* Tighten vertical spacing between stacked elements page-wide */
        div[data-testid="stVerticalBlock"] {
            gap: 0.3rem !important;
        }

        /* Pull horizontal rows (header row, metrics row, table rows) closer together */
        div[data-testid="stHorizontalBlock"] {
            margin-bottom: 0rem;
        }

        /* Material icon sizing */
        span[class^="StreamlitMaterialIcon"], .material-symbols-outlined {
            font-size: 18px;
            vertical-align: middle;
        }

        /* Header action buttons */
        .st-key-add_inv_btn button, .st-key-pdf_btn button, .st-key-excel_btn button {
            padding: 4px 10px !important;
            font-size: 13px !important;
            white-space: nowrap !important;
            height: auto !important;
        }

        /* Refresh button — square icon button to match search bar height */
        .st-key-refresh_btn button {
            padding: 4px 10px !important;
            font-size: 13px !important;
            white-space: nowrap !important;
            height: auto !important;
        }

        /* Space below metrics row (Total/Issued/Available/Damaged) */
        .st-key-metrics_row {
            margin-bottom: 1rem;
        }

        /* Space below header badges row (Brand/Model/etc) */
        .st-key-header_row {
            margin-bottom: 0.7rem;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================
# SESSION STATE
# ==========================
if "edit_row" not in st.session_state:
    st.session_state.edit_row = None

def safe_date(val):
    return val if pd.notna(val) else date.today()

# ==========================
# DATABASE FUNCTIONS
# ==========================
def fetch_inventory():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM inventory ORDER BY id DESC")
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return pd.DataFrame(rows, columns=cols)

def insert_inventory(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO inventory (
            brand, model, serial_no, item_category,
            warranty_status, quantity, status,
            hand_over_to, issue_date, received_from,
            return_date, note, status_2
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, data)

    conn.commit()
    cur.close()
    conn.close()

def update_inventory(serial_no, values):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE inventory
        SET
            brand=%s,
            model=%s,
            serial_no=%s,
            item_category=%s,
            warranty_status=%s,
            quantity=%s,
            status=%s,
            hand_over_to=%s,
            issue_date=%s,
            received_from=%s,
            return_date=%s,
            note=%s,
            status_2=%s
        WHERE serial_no=%s
    """, values)

    conn.commit()
    cur.close()
    conn.close()

def delete_inventory(serial_no):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM inventory WHERE serial_no=%s", (serial_no,))

    conn.commit()
    cur.close()
    conn.close()

# ==========================
# EXCEL EXPORT
# ==========================
def generate_inventory_excel(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        data.to_excel(writer, index=False, sheet_name="Inventory")

        # Optional: auto-fit column widths
        worksheet = writer.sheets["Inventory"]
        for i, col in enumerate(data.columns):
            max_len = max(
                data[col].astype(str).map(len).max() if not data.empty else 0,
                len(str(col))
            ) + 2
            worksheet.column_dimensions[chr(65 + i) if i < 26 else "A" + chr(65 + i - 26)].width = max_len

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

    columns = [
        "brand", "model", "serial_no", "item_category", "quantity",
        "warranty_status", "status", "hand_over_to", "issue_date",
        "received_from", "return_date", "note", "status_2",
    ]
    headers = [
        "Brand", "Model", "Serial No", "Category", "Quantity",
        "Warranty", "Status", "Handover To", "Issue Date",
        "Received From", "Return Date", "Note", "Status-2",
    ]

    table_data = [headers]
    for _, row in data.iterrows():
        line = []
        for col in columns:
            val = row.get(col, "")
            line.append(str(val) if pd.notna(val) and val != "" else "—")
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

        brand = st.selectbox("Brand", ["Dell", "Lenovo", "HP"])
        category = st.selectbox("Category", ["Laptop"])

        model = st.text_input("Model")
        serial_no = st.text_input("Serial Number")

        warranty = st.selectbox(
            "Warranty Status",
            ["Under Warranty", "Warranty Period Over", "NA"]
        )

        status = st.selectbox(
            "Status",
            ["In-Inventory", "Issued", "Damaged"]
        )

        handover = st.text_input("Handover To")
        received_from = st.text_input("Received From")

        issue_type = st.radio(
            "Issue Date Type",
            ["Date", "NA"],
            horizontal=True,
            key="add_issue_type"
        )

        issue_date = (
            st.date_input("Issue Date", value=date.today(), key="add_issue_date")
            if issue_type == "Date"
            else None
        )

        return_type = st.radio(
            "Return Date Type",
            ["Date", "NA"],
            horizontal=True,
            key="add_return_type"
        )

        return_date = (
            st.date_input("Return Date", value=date.today(), key="add_return_date")
            if return_type == "Date"
            else None
        )

        note = st.text_area("📝 Note")
        status_2 = st.text_input("Status-2")

        submit = st.form_submit_button("➕ Add Item")

        if submit:
            insert_inventory(
                (
                    brand, model, serial_no, category,
                    warranty, 1, status,
                    handover, issue_date,
                    received_from, return_date,
                    note, status_2
                )
            )
            st.success("Added Successfully")
            st.rerun()

# ==========================
# EDIT INVENTORY
# ==========================
@st.dialog("✏️ Edit Inventory")
def edit_inventory_dialog():

    row = st.session_state.edit_row

    with st.form("edit_form"):

        brand = st.selectbox(
            "Brand",
            ["Dell", "Lenovo", "HP"],
            index=["Dell", "Lenovo", "HP"].index(row["brand"])
        )

        model = st.text_input("Model", value=row["model"])
        serial = st.text_input("Serial No", value=row["serial_no"])
        category = st.text_input("Category", value=row["item_category"])

        qty = st.number_input(
            "Quantity",
            value=int(row["quantity"]),
            min_value=1
        )

        warranty = st.selectbox(
            "Warranty Status",
            ["Under Warranty", "Warranty Period Over", "NA"],
            index=["Under Warranty", "Warranty Period Over", "NA"].index(row["warranty_status"])
        )

        status = st.selectbox(
            "Status",
            ["In-Inventory", "Issued", "Damaged"],
            index=["In-Inventory", "Issued", "Damaged"].index(row["status"])
        )

        handover = st.text_input("Handover To", value=row.get("hand_over_to", ""))
        received = st.text_input("Received From", value=row.get("received_from", ""))

        issue_type = st.radio(
            "Issue Date Type",
            ["Date", "NA"],
            horizontal=True,
            index=0 if pd.notna(row["issue_date"]) else 1,
            key=f"issue_{row['id']}"
        )

        issue_date = st.date_input(
            "Issue Date",
            value=safe_date(row["issue_date"]),
            key=f"issue_date_{row['id']}"
        )

        issue_final = issue_date if issue_type == "Date" else None

        return_type = st.radio(
            "Return Date Type",
            ["Date", "NA"],
            horizontal=True,
            index=0 if pd.notna(row["return_date"]) else 1,
            key=f"return_{row['id']}"
        )

        return_date = st.date_input(
            "Return Date",
            value=safe_date(row["return_date"]),
            key=f"return_date_{row['id']}"
        )

        return_final = return_date if return_type == "Date" else None

        note = st.text_area("📝 Note", value=row.get("note", ""))

        status_2 = st.text_input("Status-2", value=row.get("status_2", ""))

        c1, c2 = st.columns(2)

        save = c1.form_submit_button("💾 Save")
        cancel = c2.form_submit_button("❌ Cancel")

        if save:
            update_inventory(
                row["serial_no"],
                (
                    brand,
                    model,
                    serial,
                    category,
                    warranty,
                    qty,
                    status,
                    handover,
                    issue_final,
                    received,
                    return_final,
                    note,
                    status_2,
                    row["serial_no"]
                )
            )
            st.success("Updated Successfully")
            st.rerun()

        if cancel:
            st.rerun()

# ==========================
# LOAD DATA
# ==========================
df = fetch_inventory()

if not df.empty:
    df.columns = df.columns.str.strip().str.lower()

# ==========================
# TOP HEADER ROW — title (left) + Add Inventory , Download PDF (right)
# ==========================

title_col, add_col, pdf_col, excel_col = st.columns(
    [6, 1.1, 1.1, 1.1],
    vertical_alignment="center"
)

with title_col:
    st.badge("**:material/inventory: Overall Inventory Status**", color='green')

with add_col:
    if st.button("Add Inventory", icon=":material/loupe:", key="add_inv_btn", use_container_width=True):
        add_inventory_dialog()

with pdf_col:
    pdf_bytes = generate_inventory_pdf(df)
    st.download_button(
        label=":material/picture_as_pdf: Download PDF",
        data=pdf_bytes,
        file_name=f"inventory-report_{date.today().strftime('%d-%m-%Y')}.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="pdf_btn",
    )

with excel_col:
    excel_bytes = generate_inventory_excel(df)
    st.download_button(
        label="📄Download Excel",
        data=excel_bytes,
        file_name=f"inventory-report_{date.today().strftime('%d-%m-%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="excel_btn",
    )

# ==========================
# METRICS
# ==========================
total = len(df)
issued = len(df[df["status"] == "Issued"]) if not df.empty else 0
available = len(df[df["status"] == "In-Inventory"]) if not df.empty else 0
damaged = len(df[df["status"] == "Damaged"]) if not df.empty else 0

with st.container(key="metrics_row"):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", total)
    c2.metric("Issued", issued)
    c3.metric("Available", available)
    c4.metric("Damaged", damaged)

# # ==========================
# # 📋 INVENTORY LIST (search box + refresh button)
# # ==========================

# search_col, refresh_col = st.columns([8, 1], vertical_alignment="bottom")

# with search_col:
#     search2 = st.text_input(
#         "Search Inventory List",
#         placeholder="🔍 Search....",
#         label_visibility="collapsed"
#     )

# with refresh_col:
#     if st.button(":material/refresh: Refresh", key="refresh_btn", use_container_width=True):
#         st.rerun()

# list_df = df.copy()

# if search2:
#     list_df = list_df[
#         list_df.apply(
#             lambda r: r.astype(str).str.contains(search2, case=False, na=False).any(),
#             axis=1
#         )
#     ]

# # ==========================
# # 📋 INVENTORY LIST (search box + refresh button)
# # ==========================

# if "search_box" not in st.session_state:
#     st.session_state.search_box = ""

# search_col, refresh_col = st.columns([8, 1], vertical_alignment="bottom")

# with search_col:
#     search2 = st.text_input(
#         "Search Inventory List",
#         placeholder="🔍 Search....",
#         label_visibility="collapsed",
#         key="search_box"
#     )

# with refresh_col:
#     if st.button(":material/refresh: Refresh", key="refresh_btn", use_container_width=True):
#         st.session_state.search_box = ""
#         st.rerun()

# list_df = df.copy()

# if search2:
#     list_df = list_df[
#         list_df.apply(
#             lambda r: r.astype(str).str.contains(search2, case=False, na=False).any(),
#             axis=1
#         )
#     ]

# ==========================
# 📋 INVENTORY LIST (search box + refresh button)
# ==========================

# Clear search BEFORE the widget is instantiated, on the rerun triggered by Refresh
if st.session_state.get("do_clear_search"):
    st.session_state.search_box = ""
    st.session_state.do_clear_search = False

search_col, refresh_col = st.columns([8, 1], vertical_alignment="bottom")

with search_col:
    search2 = st.text_input(
        "Search Inventory List",
        placeholder="🔍 Search....",
        label_visibility="collapsed",
        key="search_box"
    )

with refresh_col:
    if st.button(":material/refresh: Refresh", key="refresh_btn", use_container_width=True):
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

# column widths — used for BOTH header and data rows
COL_WIDTHS = [1.3, 1.6, 1.4, 1.5, 1.1, 1.4, 1.3, 1.4, 1.5, 1.7, 1.5, 1.8, 1.4, 0.6, 0.2, 0.6]

# Headers row

with st.container(key="header_row"):
    h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h_gap, h15 = st.columns(COL_WIDTHS)
    h1.badge("Brand")
    h2.badge("Model")
    h3.badge("Serial No.")
    h4.badge("Category")
    h5.badge("Quantity")
    h6.badge("Warranty")
    h7.badge("Status")
    h8.badge("Handover To")
    h9.badge("Issue Date")
    h10.badge("Received From")
    h11.badge("Return Date")
    h12.badge("Note")
    h13.badge("Status-2")

for _, row in list_df.iterrows():
    uid = str(row["id"])
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c_gap, c15 = st.columns(COL_WIDTHS)

    def small(val):
        return f'<p style="font-size:12px; margin:0">{val}</p>'

    c1.markdown(small(row["brand"]), unsafe_allow_html=True)
    c2.markdown(small(row["model"]), unsafe_allow_html=True)
    c3.markdown(small(row["serial_no"]), unsafe_allow_html=True)
    c4.markdown(small(row["item_category"]), unsafe_allow_html=True)
    c5.markdown(small(row["quantity"]), unsafe_allow_html=True)
    c6.markdown(small(row["warranty_status"]), unsafe_allow_html=True)
    c7.markdown(small(row["status"]), unsafe_allow_html=True)
    c8.markdown(small(row.get("hand_over_to", "")), unsafe_allow_html=True)
    c9.markdown(small(str(row["issue_date"]) if pd.notna(row["issue_date"]) else "—"), unsafe_allow_html=True)
    c10.markdown(small(row.get("received_from", "")), unsafe_allow_html=True)
    c11.markdown(small(str(row["return_date"]) if pd.notna(row["return_date"]) else "—"), unsafe_allow_html=True)
    c12.markdown(small(row.get("note", "")), unsafe_allow_html=True)
    c13.markdown(small(row.get("status_2", "")), unsafe_allow_html=True)

    if c14.button("✏️", key=f"edit_{uid}"):
        st.session_state.edit_row = row.to_dict()
        edit_inventory_dialog()

    if c15.button(":material/delete:", key=f"del_{uid}"):
        delete_inventory(row["serial_no"])
        st.warning("Deleted")
        st.rerun()

st.divider()
# ----------------------------
# Footer
# ----------------------------
st.caption("Inventory Management System • Dashboard")