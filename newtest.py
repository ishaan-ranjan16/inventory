# import streamlit as st
# import pandas as pd
# from datetime import date, datetime

# from db_connection import get_connection
# from streamlit_searchbox import st_searchbox

# st.set_page_config(page_title="Inventory", layout="wide")

# st.markdown("""
# <style>
# html { zoom: 72%; }
# .block-container { padding-top: 0rem; padding-bottom: 0rem; }
# header[data-testid="stHeader"] { display: none; }
# [data-testid="stDecoration"] { display: none; }
# </style>
# """, unsafe_allow_html=True)

# # ======================
# # SESSION STATE
# # ======================
# for k in ["edit_row", "delete_id", "delete_label"]:
#     if k not in st.session_state:
#         st.session_state[k] = None


# # ======================
# # CONFIG
# # ======================
# COL_WIDTHS = [0.5, 1.2, 1.2, 1.5, 1.2, 0.8, 1, 1, 1.2, 1.2, 1.2, 1.2, 1.5, 1, 0.6, 0.6]


# # ======================
# # HELPERS
# # ======================
# def safe_val(val):
#     if val is None or str(val).strip() == "":
#         return "—"
#     if isinstance(val, float) and pd.isna(val):
#         return "—"
#     return str(val)


# def safe_date_str(val):
#     if val is None or str(val).strip() in ("", "None", "NaT"):
#         return "—"
#     return str(val)


# # ======================
# # DB
# # ======================
# def fetch_inventory():
#     conn = get_connection()
#     cur = conn.cursor()

#     cur.execute("""
#         SELECT id, brand, model, serial_no, item_category, quantity,
#                warranty_status, status, hand_over_to, issue_date,
#                received_from, return_date, note, status_2
#         FROM inventory
#         ORDER BY id DESC
#     """)

#     rows = cur.fetchall()
#     conn.close()

#     cols = [
#         "id","brand","model","serial_no","item_category","quantity",
#         "warranty_status","status","hand_over_to","issue_date",
#         "received_from","return_date","note","status_2"
#     ]

#     return pd.DataFrame(rows, columns=cols)


# def search_inventory_items(searchterm: str):
#     conn = get_connection()
#     cur = conn.cursor()

#     if not searchterm:
#         cur.execute("""
#             SELECT brand || ' - ' || model || ' (SN: ' || serial_no || ')'
#             FROM inventory
#             ORDER BY id DESC
#             LIMIT 10
#         """)
#     else:
#         cur.execute("""
#             SELECT brand || ' - ' || model || ' (SN: ' || serial_no || ')'
#             FROM inventory
#             WHERE brand LIKE ?
#                OR model LIKE ?
#                OR serial_no LIKE ?
#             LIMIT 10
#         """, (f"%{searchterm}%", f"%{searchterm}%", f"%{searchterm}%"))

#     results = [r[0] for r in cur.fetchall()]
#     conn.close()
#     return results


# # ======================
# # LOAD DATA
# # ======================
# df = fetch_inventory()

# if not df.empty:
#     df.columns = df.columns.str.lower()


# # ======================
# # SEARCHBOX
# # ======================
# search_selected = st_searchbox(
#     search_inventory_items,
#     placeholder="Search inventory (brand / model / serial)...",
#     key="inventory_search"
# )

# free_text = st.session_state.get("inventory_search", "")
# search_value = search_selected or free_text


# # ======================
# # FILTER
# # ======================
# list_df = df.copy().fillna("")

# if search_value and search_value.strip():
#     mask = list_df.astype(str).apply(
#         lambda col: col.str.contains(search_value, case=False, na=False, regex=False)
#     ).any(axis=1)

#     list_df = list_df[mask]

# list_df = list_df.reset_index(drop=True)
# list_df["s_no"] = list_df.index + 1


# # ======================
# # HEADER
# # ======================
# headers = [
#     "S.No", "Brand", "Model", "Serial", "Category", "Qty",
#     "Warranty", "Status", "Handover", "Issue Date",
#     "Received", "Return Date", "Note", "Status-2", "Edit", "Del"
# ]

# with st.container():
#     cols = st.columns(COL_WIDTHS)

#     for i, h in enumerate(headers):
#         cols[i].markdown(f"**{h}**")


# # ======================
# # ROWS
# # ======================
# def cell(col, value):
#     col.markdown(f"<p style='font-size:12px;margin:0'>{safe_val(value)}</p>", unsafe_allow_html=True)


# for _, row in list_df.iterrows():
#     uid = str(row["id"])

#     c = st.columns(COL_WIDTHS)

#     cell(c[0], row["s_no"])
#     cell(c[1], row["brand"])
#     cell(c[2], row["model"])
#     cell(c[3], row["serial_no"])
#     cell(c[4], row["item_category"])
#     cell(c[5], row["quantity"])
#     cell(c[6], row["warranty_status"])
#     cell(c[7], row["status"])
#     cell(c[8], row.get("hand_over_to"))
#     cell(c[9], row["issue_date"])
#     cell(c[10], row.get("received_from"))
#     cell(c[11], row["return_date"])
#     cell(c[12], row.get("note"))
#     cell(c[13], row.get("status_2"))

#     if c[14].button("✏️", key=f"edit_{uid}"):
#         st.session_state.edit_row = row.to_dict()
#         st.info("Edit clicked (dialog not implemented)")

#     if c[15].button("🗑️", key=f"del_{uid}"):
#         st.session_state.delete_id = row["id"]
#         st.session_state.delete_label = f'{row["brand"]} - {row["model"]}'
#         st.warning("Delete clicked (dialog not implemented)")


# st.divider()
# st.caption("Inventory Management System • Dashboard")

import streamlit as st
import pandas as pd
from datetime import date, datetime
import io
import time
from db_connection import get_connection

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


st.set_page_config(page_title="Inventory", layout="wide")

# =============================
# SMART AUTOCOMPLETE HELPER
# =============================
def smart_suggestions(options, key, label):
    if not options:
        return

    query = st.session_state.get(key, "")

    if query:
        filtered = [o for o in options if query.lower() in str(o).lower()]
    else:
        filtered = options[:8]

    if filtered:
        st.caption(f"{label} suggestions")
        cols = st.columns(min(4, len(filtered[:4])))

        for i, val in enumerate(filtered[:4]):
            col = cols[i % len(cols)]
            if col.button(str(val), key=f"{key}_sug_{i}"):
                st.session_state[key] = val
                st.rerun()


# =============================
# SESSION STATE
# =============================
if "edit_row" not in st.session_state:
    st.session_state.edit_row = None

if "delete_id" not in st.session_state:
    st.session_state.delete_id = None

if "delete_label" not in st.session_state:
    st.session_state.delete_label = ""

if "show_add_dialog" not in st.session_state:
    st.session_state.show_add_dialog = False

if "add_errors" not in st.session_state:
    st.session_state.add_errors = {}


# =============================
# DATE HELPERS
# =============================
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
        return val.strftime("%d-%m-%Y")
    if isinstance(val, date):
        return val.strftime("%d-%m-%Y")
    if isinstance(val, str):
        try:
            datetime.strptime(val, "%d-%m-%Y")
            return val
        except ValueError:
            return None
    return None

# =============================
# DB FUNCTIONS
# =============================
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


def insert_inventory(data):
    conn = get_connection()
    cur = conn.cursor()

    data = list(data)
    data[8] = _safe_date_str(data[8])
    data[10] = _safe_date_str(data[10])

    cur.execute("""
        INSERT INTO inventory (
            brand, model, serial_no, item_category,
            warranty_status, quantity, status,
            hand_over_to, issue_date, received_from,
            return_date, note, status_2
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple(data))

    conn.commit()
    cur.close()
    conn.close()


def update_inventory(values):
    conn = get_connection()
    cur = conn.cursor()

    values = list(values)
    values[8] = _safe_date_str(values[8])
    values[10] = _safe_date_str(values[10])

    cur.execute("""
        UPDATE inventory
        SET brand=?, model=?, serial_no=?, item_category=?,
            warranty_status=?, quantity=?, status=?,
            hand_over_to=?, issue_date=?, received_from=?,
            return_date=?, note=?, status_2=?
        WHERE id=?
    """, tuple(values))

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


# =============================
# DISTINCT VALUES (AUTOCOMPLETE DATA SOURCE)
# =============================
def fetch_distinct(column):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT DISTINCT {column} FROM inventory WHERE {column} IS NOT NULL")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows if r[0]]

@st.dialog("📝 Add Inventory", width="large")
def add_inventory_dialog():

    brand_options = fetch_distinct("brand")
    model_options = fetch_distinct("model")
    serial_options = fetch_distinct("serial_no")
    warranty_options = fetch_distinct("warranty_status")
    status_options = fetch_distinct("status")
    received_options = fetch_distinct("received_from")

    with st.form("add_form"):

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.text_input("Enter Brand", key="add_brand")
            smart_suggestions(brand_options, "add_brand", "Brand")

        with c2:
            st.text_input("Category", value="Laptop", key="add_category")

        with c3:
            st.text_input("Enter Model", key="add_model")
            smart_suggestions(model_options, "add_model", "Model")

        with c4:
            st.text_input("Enter Serial Number", key="add_serial")
            smart_suggestions(serial_options, "add_serial", "Serial No")

        st.markdown("---")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.number_input("Quantity", min_value=1, value=1, key="add_qty")

        with c2:
            st.text_input("Warranty Status", key="add_warranty")
            smart_suggestions(warranty_options, "add_warranty", "Warranty")

        with c3:
            st.text_input("Status", key="add_status")
            smart_suggestions(status_options, "add_status", "Status")

        with c4:
            st.text_input("Status-2", key="add_status2")

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:
            st.text_input("Handover To", key="add_handover")

        with c2:
            st.text_input("Received From", key="add_received")
            smart_suggestions(received_options, "add_received", "Received From")

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:
            issue_type = st.radio("Issue Date", ["Set Date", "NA"], horizontal=True, key="add_issue_type")
            if issue_type == "Set Date":
                st.date_input("Issue Date", value=date.today(), key="add_issue_date")

        with c2:
            return_type = st.radio("Return Date", ["Set Date", "NA"], horizontal=True, key="add_return_type")
            if return_type == "Set Date":
                st.date_input("Return Date", value=date.today(), key="add_return_date")

        st.text_area("Note", key="add_note")

        c1, c2 = st.columns(2)
        submit = c1.form_submit_button("Save")
        cancel = c2.form_submit_button("Cancel")

    if cancel:
        st.rerun()

    if submit:
        insert_inventory((
            st.session_state.get("add_brand", ""),
            st.session_state.get("add_model", ""),
            st.session_state.get("add_serial", ""),
            st.session_state.get("add_category", ""),
            st.session_state.get("add_warranty", ""),
            st.session_state.get("add_qty", 1),
            st.session_state.get("add_status", ""),
            st.session_state.get("add_handover", ""),
            st.session_state.get("add_issue_date", None),
            st.session_state.get("add_received", ""),
            st.session_state.get("add_return_date", None),
            st.session_state.get("add_note", ""),
            st.session_state.get("add_status2", ""),
        ))

        st.success("Saved successfully!")
        time.sleep(0.5)
        st.rerun()

@st.dialog("✏️ Edit Inventory", width="large")
def edit_inventory_dialog():
    row = st.session_state.edit_row

    with st.form("edit_form"):
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            brand = st.text_input("Brand", value=row["brand"])
        with c2:
            category = st.text_input("Category", value=row["item_category"])
        with c3:
            model = st.text_input("Model", value=row["model"])
        with c4:
            serial = st.text_input("Serial No", value=row["serial_no"])

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:
            qty = st.number_input("Quantity", value=int(row["quantity"] or 1), min_value=1)
        with c2:
            status = st.text_input("Status", value=row["status"] or "")

        note = st.text_area("Note", value=row.get("note") or "")

        c1, c2 = st.columns(2)
        save = c1.form_submit_button("Save")
        cancel = c2.form_submit_button("Cancel")

    if save:
        update_inventory((
            brand, model, serial, category,
            row["warranty_status"], qty, status,
            row["hand_over_to"], row["issue_date"],
            row["received_from"], row["return_date"],
            note, row["status_2"],
            row["id"]
        ))
        st.success("Updated successfully!")
        time.sleep(0.5)
        st.rerun()

    if cancel:
        st.rerun()

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

# # =============================
# # DELETE DIALOG
# # =============================
# @st.dialog("Delete")
# def confirm_delete_dialog():
#     item_id = st.session_state.delete_id

#     st.warning("Delete this item?")

#     c1, c2 = st.columns(2)
#     with c1:
#         if st.button("Yes"):
#             delete_inventory(item_id)
#             st.rerun()
#     with c2:
#         if st.button("No"):
#             st.rerun()

# CONFIRM DELETE DIALOG-
# =====================
@st.dialog("🗑️ Confirm Delete")
def confirm_delete_dialog():
    item_id    = st.session_state.delete_id
    item_label = st.session_state.delete_label
    st.warning("Are you sure you want to delete this item?")
    st.markdown(
        f'<p style="font-size:13px; margin: 4px 0 12px 0;">'
        f'<b>Item:</b> {item_label}</p>',
        unsafe_allow_html=True
    )
    st.caption("This action cannot be undone.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Yes, Delete", type="primary", use_container_width=True):
            delete_inventory(item_id)
            st.session_state.delete_id    = None
            st.session_state.delete_label = ""
            st.info("#### 🗑️ Deleted Successfully!")
            time.sleep(0.5)
            st.rerun()

    with c2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.delete_id    = None
            st.session_state.delete_label = ""
            st.rerun()

# LOAD DATA
# ==========================
def load_data():
    return fetch_inventory()

df = load_data()

if not df.empty:
    df.columns = df.columns.str.strip().str.lower()

# TOP HEADER ROW
# ==========================
title_col, add_col, pdf_col, excel_col = st.columns(
    [6, 1.1, 1.1, 1.1], vertical_alignment="center"
)

with title_col:
    st.badge("**:material/inventory: Overall Inventory Status**", color='green')

with add_col:
    if st.button(
        "Add Inventory",
        icon=":material/add_box:",
        key="add_inv_btn",
        use_container_width=True,
    ):
        st.session_state.show_add_dialog = True

if st.session_state.get("show_add_dialog", False):
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

# METRICS
# ================
total     = len(df)
Issued    = len(df[df["status"].str.lower().isin(["issued", "given"])])
Available = len(df[df["status"].str.lower().isin(["in-inventory", "inventory"])])
Damaged   = len(df[df["status"].str.lower().isin(["damaged", "maintainance"])])

with st.container(key="metrics_row"):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total",        total)
    c2.metric("Issued",       Issued)
    c3.metric("In-Inventory", Available)
    c4.metric("Damaged",      Damaged)

# SEARCH + REFRESH
# ==========================
if st.session_state.get("do_clear_search"):
    st.session_state.search_box = ""
    st.session_state.do_clear_search = False
    st.rerun()

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