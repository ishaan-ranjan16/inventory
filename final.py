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
from openpyxl.utils import get_column_letter


st.set_page_config(page_title="Inventory", layout="wide")


# =========================
# SESSION STATE
# =========================
for k in [
    "edit_row",
    "delete_id",
    "delete_label",
    "show_add_dialog",
    "show_edit_dialog",
    "show_delete_dialog",
    "add_errors",
]:
    if k not in st.session_state:
        st.session_state[k] = None if "row" in k or "id" in k else False if "show" in k else {}


# =========================
# HELPERS
# =========================
def safe_val(val):
    if val is None or str(val).strip() == "" or pd.isna(val):
        return "—"
    return str(val)


def safe_date_str(val):
    if val is None or str(val).strip() in ("", "None", "NaT"):
        return None
    return val


def safe_date(val):
    if val is None or str(val).strip() == "":
        return date.today()
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        try:
            return datetime.strptime(val, "%d-%m-%Y").date()
        except:
            return date.today()
    return val


# =========================
# DB FUNCTIONS
# =========================
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


def fetch_distinct(col):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT DISTINCT {col} FROM inventory WHERE {col} IS NOT NULL")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]


def insert_inventory(data):
    conn = get_connection()
    cur = conn.cursor()

    data = list(data)
    data[8] = safe_date_str(data[8])
    data[10] = safe_date_str(data[10])

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
    conn.close()


def update_inventory(values):
    conn = get_connection()
    cur = conn.cursor()

    values = list(values)
    values[8] = safe_date_str(values[8])
    values[10] = safe_date_str(values[10])

    cur.execute("""
        UPDATE inventory SET
            brand=?, model=?, serial_no=?, item_category=?,
            warranty_status=?, quantity=?, status=?,
            hand_over_to=?, issue_date=?, received_from=?,
            return_date=?, note=?, status_2=?
        WHERE id=?
    """, tuple(values))

    conn.commit()
    conn.close()


def delete_inventory(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventory WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


# =========================
# AUTOCOMPLETE
# =========================
def smart_suggestions(options, key, label):
    if not options:
        return

    q = st.session_state.get(key, "")

    filtered = [o for o in options if q.lower() in str(o).lower()] if q else options[:6]

    cols = st.columns(min(4, len(filtered[:4])))

    for i, v in enumerate(filtered[:4]):
        if cols[i].button(str(v), key=f"{key}_{i}"):
            st.session_state[key] = v
            st.rerun()


# =========================
# ADD DIALOG
# =========================
@st.dialog("📝 Add Inventory")
def add_inventory_dialog():

    brands = fetch_distinct("brand")
    models = fetch_distinct("model")
    serials = fetch_distinct("serial_no")

    with st.form("add_form"):

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.text_input("Brand", key="add_brand")
            smart_suggestions(brands, "add_brand", "Brand")

        with c2:
            st.text_input("Category", value="Laptop", key="add_category")

        with c3:
            st.text_input("Model", key="add_model")
            smart_suggestions(models, "add_model", "Model")

        with c4:
            st.text_input("Serial No", key="add_serial")
            smart_suggestions(serials, "add_serial", "Serial")

        st.number_input("Quantity", min_value=1, value=1, key="add_qty")
        st.text_input("Status", key="add_status")
        st.text_input("Status-2", key="add_status2")
        st.text_input("Handover To", key="add_handover")
        st.text_input("Received From", key="add_received")
        st.text_area("Note", key="add_note")

        submit = st.form_submit_button("Save")
        cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.show_add_dialog = False
        st.rerun()

    if submit:
        insert_inventory((
            st.session_state.add_brand,
            st.session_state.add_model,
            st.session_state.add_serial,
            st.session_state.add_category,
            "",
            st.session_state.add_qty,
            st.session_state.add_status,
            st.session_state.add_handover,
            None,
            st.session_state.add_received,
            None,
            st.session_state.add_note,
            st.session_state.add_status2,
        ))

        st.success("Saved!")
        st.rerun()


# =========================
# EDIT DIALOG
# =========================
@st.dialog("✏️ Edit Inventory")
def edit_inventory_dialog():

    row = st.session_state.edit_row

    with st.form("edit_form"):

        brand = st.text_input("Brand", value=row["brand"])
        model = st.text_input("Model", value=row["model"])
        serial = st.text_input("Serial", value=row["serial_no"])
        category = st.text_input("Category", value=row["item_category"])

        qty = st.number_input("Qty", value=int(row["quantity"] or 1))
        status = st.text_input("Status", value=row["status"] or "")
        note = st.text_area("Note", value=row.get("note") or "")

        save = st.form_submit_button("Save")
        cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.show_edit_dialog = False
        st.rerun()

    if save:
        update_inventory((
            brand, model, serial, category,
            row["warranty_status"], qty, status,
            row["hand_over_to"], row["issue_date"],
            row["received_from"], row["return_date"],
            note, row["status_2"],
            row["id"]
        ))

        st.success("Updated!")
        st.rerun()


# =========================
# DELETE DIALOG
# =========================
@st.dialog("🗑️ Delete Item")
def delete_dialog():

    st.warning("Delete this item?")
    st.write(st.session_state.delete_label)

    c1, c2 = st.columns(2)

    if c1.button("Yes"):
        delete_inventory(st.session_state.delete_id)
        st.rerun()

    if c2.button("No"):
        st.session_state.show_delete_dialog = False
        st.rerun()


df = fetch_inventory()

if not df.empty:
    df.columns = df.columns.str.lower()


# =========================
# HEADER
# =========================
c1, c2 = st.columns([6, 1])

with c1:
    st.title("📦 Inventory System")

with c2:
    if st.button("➕ Add"):
        st.session_state.show_add_dialog = True


if st.session_state.show_add_dialog:
    add_inventory_dialog()

if st.session_state.show_edit_dialog:
    edit_inventory_dialog()

if st.session_state.show_delete_dialog:
    delete_dialog()


# =========================
# SEARCH
# =========================
search = st.text_input("Search Inventory")

filtered = df.copy()

if search:
    filtered = filtered[
        filtered.astype(str).apply(lambda c: c.str.contains(search, case=False)).any(axis=1)
    ]

filtered = filtered.reset_index(drop=True)
filtered["s_no"] = filtered.index + 1


# =========================
# TABLE
# =========================
for _, row in filtered.iterrows():

    c = st.columns([1,2,2,2,2,1,1])

    c[0].write(row["s_no"])
    c[1].write(row["brand"])
    c[2].write(row["model"])
    c[3].write(row["serial_no"])
    c[4].write(row["status"])

    if c[5].button("✏️", key=f"e{row['id']}"):
        st.session_state.edit_row = row.to_dict()
        st.session_state.show_edit_dialog = True
        st.rerun()

    if c[6].button("🗑️", key=f"d{row['id']}"):
        st.session_state.delete_id = row["id"]
        st.session_state.delete_label = f"{row['brand']} - {row['model']}"
        st.session_state.show_delete_dialog = True
        st.rerun()

# =========================
# METRICS (OPTIONAL CLEAN VIEW)
# =========================
st.divider()

total = len(df)
issued = len(df[df["status"].str.lower().isin(["issued", "given"])])
available = len(df[df["status"].str.lower().isin(["in-inventory", "inventory"])])
damaged = len(df[df["status"].str.lower().isin(["damaged", "maintenance"])])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", total)
c2.metric("Issued", issued)
c3.metric("Available", available)
c4.metric("Damaged", damaged)


# =========================
# EXPORT HELPERS
# =========================
def generate_excel(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()

    export_df = data.copy()

    cols = [
        "brand", "model", "serial_no", "item_category", "quantity",
        "warranty_status", "status", "hand_over_to",
        "issue_date", "received_from", "return_date",
        "note", "status_2"
    ]

    export_df = export_df[cols]
    export_df.insert(0, "s_no", range(1, len(export_df) + 1))

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Inventory")

        sheet = writer.sheets["Inventory"]

        for i, col in enumerate(export_df.columns):
            max_len = max(export_df[col].astype(str).map(len).max(), len(col)) + 2
            sheet.column_dimensions[get_column_letter(i + 1)].width = max_len

    buffer.seek(0)
    return buffer.getvalue()


def generate_pdf(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Inventory Report", styles["Title"]))
    elements.append(Spacer(1, 10))

    cols = [
        "brand", "model", "serial_no", "item_category", "quantity",
        "warranty_status", "status", "hand_over_to",
        "issue_date", "received_from", "return_date",
        "note", "status_2"
    ]

    table_data = [["S.No"] + cols]

    for i, row in data.iterrows():
        table_data.append(
            [i + 1] + [safe_val(row[c]) for c in cols]
        )

    table = Table(table_data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer.getvalue()


# =========================
# EXPORT BUTTONS
# =========================
c1, c2 = st.columns(2)

with c1:
    st.download_button(
        "⬇️ Download Excel",
        generate_excel(df),
        file_name="inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with c2:
    st.download_button(
        "⬇️ Download PDF",
        generate_pdf(df),
        file_name="inventory.pdf",
        mime="application/pdf"
    )


# =========================
# FOOTER
# =========================
st.divider()
st.caption("📦 Inventory Management System • Streamlit App")