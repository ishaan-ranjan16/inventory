# test - Smart text (brand
# model
# serial no
# warranty status
# status
# received from)
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

from streamlit_smart_text_input import st_smart_text_input

st.set_page_config(page_title="Inventory", layout="wide")

# ==========================
# CACHE DISTINCT VALUES (SMART AUTOCOMPLETE)
# ==========================
@st.cache_data(ttl=300)
def fetch_distinct(column):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT DISTINCT {column} FROM inventory WHERE {column} IS NOT NULL")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows if r[0]]

# ==========================
# DATE HELPERS
# ==========================
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
        try:
            datetime.strptime(val, '%d-%m-%Y')
            return val
        except ValueError:
            return None
    return None

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
        st.error("Database connection error")
        return pd.DataFrame(columns=columns)


def insert_inventory(data):
    conn = get_connection()
    cur = conn.cursor()

    clean_data = list(data)
    clean_data[8] = _safe_date_str(clean_data[8])
    clean_data[10] = _safe_date_str(clean_data[10])

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
    clean_values[8] = _safe_date_str(clean_values[8])
    clean_values[10] = _safe_date_str(clean_values[10])

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

def generate_inventory_pdf(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Inventory Report", styles["Title"]))
    elements.append(Spacer(1, 10))

    data = data.reset_index(drop=True)

    table_data = [["S.No", "Brand", "Model", "Serial No"]]

    for i, row in data.iterrows():
        table_data.append([
            str(i + 1),
            str(row["brand"]),
            str(row["model"]),
            str(row["serial_no"])
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black)
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer.getvalue()

def generate_inventory_excel(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        data.to_excel(writer, index=False, sheet_name="Inventory")

    buffer.seek(0)
    return buffer.getvalue()

@st.dialog("📝 Add Inventory", width="large")
def add_inventory_dialog():

    # 🔥 FETCH OPTIONS FROM DB (AUTOCOMPLETE)
    brand_options = fetch_distinct("brand")
    model_options = fetch_distinct("model")
    serial_options = fetch_distinct("serial_no")
    warranty_options = fetch_distinct("warranty_status")
    status_options = fetch_distinct("status")
    received_options = fetch_distinct("received_from")

    with st.form("add_form"):

        # ROW 1
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            add_brand = st_smart_text_input(
                label="Brand",
                options=brand_options,
                placeholder="Type or select brand...",
                key="add_brand"
            )

        with c2:
            st.text_input("Category", value="Laptop", key="add_category")

        with c3:
            add_model = st_smart_text_input(
                label="Model",
                options=model_options,
                placeholder="Type or select model...",
                key="add_model"
            )

        with c4:
            add_serial = st_smart_text_input(
                label="Serial No",
                options=serial_options,
                placeholder="Type or select serial...",
                key="add_serial"
            )

        st.markdown("---")

        # ROW 2
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.number_input("Quantity", min_value=1, value=1, key="add_qty")

        with c2:
            add_warranty = st_smart_text_input(
                label="Warranty Status",
                options=warranty_options,
                placeholder="Warranty info...",
                key="add_warranty"
            )

        with c3:
            add_status = st_smart_text_input(
                label="Status",
                options=status_options,
                placeholder="Issued / In-Inventory...",
                key="add_status"
            )

        with c4:
            st.text_input("Status-2", key="add_status2")

        st.markdown("---")

        # ROW 3
        c1, c2 = st.columns(2)

        with c1:
            st.text_input("Handover To", key="add_handover")

        with c2:
            add_received = st_smart_text_input(
                label="Received From",
                options=received_options,
                placeholder="Vendor / Person...",
                key="add_received"
            )

        st.markdown("---")

        # ROW 4
        c1, c2 = st.columns(2)

        with c1:
            issue_type = st.radio(
                "Issue Date",
                ["Set Date", "NA"],
                horizontal=True,
                key="add_issue_type"
            )
            if issue_type == "Set Date":
                st.date_input("Issue Date", value=date.today(), key="add_issue_date")

        with c2:
            return_type = st.radio(
                "Return Date",
                ["Set Date", "NA"],
                horizontal=True,
                key="add_return_type"
            )
            if return_type == "Set Date":
                st.date_input("Return Date", value=date.today(), key="add_return_date")

        st.text_area("Note", key="add_note")

        # BUTTONS
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

# EDIT INVENTORY DIALOG
# ==========================
@st.dialog("✏️ Edit Inventory", width="large")
def edit_inventory_dialog():
    row = st.session_state.edit_row

    with st.form("edit_form"):
        # — Row 1: Brand | Category | Model | Serial No —
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        with r1c1:
            brand = st.text_input("Brand", value=row["brand"])
        with r1c2:
            category = st.text_input("Category", value=row["item_category"])
        with r1c3:
            model = st.text_input("Model", value=row["model"])
        with r1c4:
            serial = st.text_input("Serial No.", value=row["serial_no"])
        st.markdown("<hr style='margin: 6px 0;'>", unsafe_allow_html=True)

        # — Row 2: Qty | Warranty | Status | Status-2 —
        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        with r2c1:
            qty = st.number_input(
                "Quantity",
                value=int(row["quantity"]) if row["quantity"] is not None else 1,
                min_value=1
            )
        with r2c2:
            warranty = st.text_input("Warranty Status", value=row["warranty_status"] or "")
        with r2c3:
            status = st.text_input("Status", value=row["status"] or "")
        with r2c4:
            status_2 = st.text_input("Status-2", value=row.get("status_2") or "")
        st.markdown("<hr style='margin: 6px 0;'>", unsafe_allow_html=True)

        # — Row 3: Handover To | Received From —
        r3c1, r3c2 = st.columns(2)
        with r3c1:
            handover = st.text_input("Handover To", value=row.get("hand_over_to") or "")
        with r3c2:
            received = st.text_input("Received From", value=row.get("received_from") or "")

        st.markdown("<hr style='margin: 6px 0;'>", unsafe_allow_html=True)

        # — Row 4: Issue Date | Return Date —
        r4c1, r4c2 = st.columns(2)
        with r4c1:
            issue_type = st.radio(
                "📅 Issue Date", ["Set Date", "NA (not issued/in-inventory/available)"],
                horizontal=True,
                index=0 if row["issue_date"] else 1,
                key=f"issue_{row['id']}"
            )
            issue_date = st.date_input(
                "Issue Date",
                value=safe_date(row["issue_date"]),
                key=f"issue_date_{row['id']}",
                label_visibility="collapsed"
            )
            issue_final = issue_date if issue_type == "Set Date" else None

        with r4c2:
            return_type = st.radio(
                "📅 Return Date", ["Set Date", "NA (in-inventory/not returned/in-use)"],
                horizontal=True,
                index=0 if row["return_date"] else 1,
                key=f"return_{row['id']}"
            )
            return_date = st.date_input(
                "Return Date",
                value=safe_date(row["return_date"]),
                key=f"return_date_{row['id']}",
                label_visibility="collapsed"
            )
            return_final = return_date if return_type == "Set Date" else None

        st.markdown("<hr style='margin: 6px 0;'>", unsafe_allow_html=True)
        # — Row 5: Note —
        note = st.text_area("📝 Note", value=row.get("note") or "", height=80)
        c1, c2 = st.columns(2)
        save   = c1.form_submit_button("💾 Save",    use_container_width=True)
        cancel = c2.form_submit_button("❌ Cancel", use_container_width=True)

    if save:
        update_inventory((
            brand, model, serial, category,
            warranty, qty, status,
            handover, issue_final,
            received, return_final,
            note, status_2,
            row["id"]
        ))
        st.success("#### ✅ Updated Successfully!")
        time.sleep(0.5)
        st.rerun()

    if cancel:
        st.rerun()

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