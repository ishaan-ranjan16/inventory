import streamlit as st
import pandas as pd
from datetime import date
import io
from db_connection import get_connection

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


st.set_page_config(page_title="Inventory Status", layout="wide")
st.badge("**:material/inventory: Inventory Status**",color='green')
# st.markdown("### 🏬 **Inventory Status** :green[Active]") 
# Or using a block background:
# st.markdown("##🏬 Inventory Status ** :material/inventory:")

# col_spacer, col_btn = st.columns([6.3, 1])
# with col_btn:
#     if st.button("➕ Add Inventory"):
#         add_inventory_dialog() 
        

import streamlit as st

st.markdown("""
    <style>
        /* Remove the default top padding above your content */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        /* Hide the Streamlit header bar entirely (hamburger menu, deploy button) */
        header[data-testid="stHeader"] {
            display: none;
        }

        /* Hide the colored decoration line under the header */
        [data-testid="stDecoration"] {
            display: none;
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
    elements.append(Paragraph(f"Generated on {date.today().strftime('%d-%m-%Y')}", styles["Normal"]))
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
# ADD INVENTORY --
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
# EDIT INVENTORY -
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
            key=f"issue_{row['id']}"   # ✅ FIX: use id NOT serial_no
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
            key=f"return_{row['id']}"   # ✅ FIX
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



# col_spacer, col_btn = st.columns([6.3, 1])
# with col_btn:
#     if st.button("➕ Add Inventory"):
#         add_inventory_dialog() 

# ==========================
# METRICS --
# ==========================
total = len(df)
issued = len(df[df["status"] == "Issued"]) if not df.empty else 0
available = len(df[df["status"] == "In-Inventory"]) if not df.empty else 0
damaged = len(df[df["status"] == "Damaged"]) if not df.empty else 0

st.markdown("""
<style>
div[data-testid="stMetricValue"] {
    font-size: 15px;
}
div[data-testid="stMetricLabel"] {
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", total)
c2.metric("Issued", issued)
c3.metric("Available", available)
c4.metric("Damaged", damaged)


# st.divider()

# ==========================
# ➕ ADD INVENTORY -
# ==========================
col_spacer, col_btn = st.columns([6.1, 1])
with col_btn:
    if st.button("➕ Add Inventory"):
        add_inventory_dialog()

# # ==========================
# # 📋 INVENTORY LIST (with EDIT + DELETE)
# # ==========================
# st.badge("**📋 Inventory List**",color='orange')

# search_col, dl_col = st.columns([3, 1])

# # with search_col:
# #     search2 = st.text_input("🔍Search Inventory List")
# with search_col:
#     search2 = st.text_input(
#         "Search Inventory List",
#         placeholder="🔍 Search....",
#         label_visibility="collapsed"
#     )

# list_df = df.copy()

# if search2:
#     list_df = list_df[
#         list_df.apply(
#             lambda r: r.astype(str).str.contains(search2, case=False, na=False).any(),
#             axis=1
#         )
#     ]

# # st.divider()

# # with dl_col:
# #     st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
# #     pdf_bytes = generate_inventory_pdf(list_df)
# #     st.download_button(
# #         label="📄 Download PDF",
# #         data=pdf_bytes,
# #         file_name=f"inventory-report_{date.today().strftime('%d-%m-%Y')}.pdf",
# #         mime="application/pdf",
# #     )

# with dl_col:
#     st.markdown("<div style='margin-top:2px'></div>", unsafe_allow_html=True)  # tweak this value (try 0, 2, 4px)
#     pdf_bytes = generate_inventory_pdf(list_df)
#     st.download_button(
#         label="📄 Download PDF",
#         data=pdf_bytes,
#         file_name=f"inventory-report_{date.today().strftime('%d-%m-%Y')}.pdf",
#         mime="application/pdf",
#     )
# col_spacer, col_btn = st.columns([6.3, 1])
# with col_btn:
#     if st.button("➕ Add Inventory"):
#         add_inventory_dialog()

# ==========================
# 📋 INVENTORY LIST (with EDIT + DELETE)
# ==========================
st.badge("**📋 Inventory List**", color='orange')

# search_col, dl_col, end_spacer = st.columns([4, 2, 4])

# with search_col:
#     search2 = st.text_input(
#         "Search Inventory List",
#         placeholder="🔍 Search....",
#         label_visibility="collapsed"
#     )

# list_df = df.copy()

# if search2:
#     list_df = list_df[
#         list_df.apply(
#             lambda r: r.astype(str).str.contains(search2, case=False, na=False).any(),
#             axis=1
#         )
#     ]

# with dl_col:
#     pdf_bytes = generate_inventory_pdf(list_df)
#     st.download_button(
#         label="📄 Download PDF",
#         data=pdf_bytes,
#         file_name=f"inventory-report_{date.today().strftime('%d-%m-%Y')}.pdf",
#         mime="application/pdf",
#     )

    # search_col, dl_col = st.columns([6.3, 1])
search_col, end_spacer, dl_col = st.columns([14.3, 0.1, 2.5])
with search_col:
    search2 = st.text_input(
        "Search Inventory List",
        placeholder="🔍 Search....",
        label_visibility="collapsed"
    )

list_df = df.copy()

if search2:
    list_df = list_df[
        list_df.apply(
            lambda r: r.astype(str).str.contains(search2, case=False, na=False).any(),
            axis=1
        )
    ]

with dl_col:
    pdf_bytes = generate_inventory_pdf(list_df)
    st.download_button(
        label="📄 Download PDF",
        data=pdf_bytes,
        file_name=f"inventory-report_{date.today().strftime('%d-%m-%Y')}.pdf",
        mime="application/pdf",
    )

# Change the headers line - add a spacer column
h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h_gap, h15 = st.columns([1.5, 1.5, 1.5, 1.5, 1, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 2, 1.5, 0.7, 0.2, 0.7])
h1.badge("Brd.")
h2.badge("Mod.")
h3.badge("S.No")
h4.badge("Category")
h5.badge("Qty.")
h6.badge("Wty.")
h7.badge("Status")
h8.badge("H/O to.")
h9.badge("D.O.I.")
h10.badge("Rec.from")
h11.badge("D.O.R.")
h12.badge("Note")
h13.badge("Status-2")
# h14.badge("edit")
# # h_gap is intentionally left empty
# h15.badge("Del.")

# st.divider()

for _, row in list_df.iterrows():
    uid = str(row["id"])

    # Add h_gap spacer column here too
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c_gap, c15 = st.columns([1.5, 1.5, 1.5, 1.5, 1, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 2, 1.5, 0.5, 0.4, 0.5])

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

    # c_gap is left empty — acts as spacer

    if c15.button("🗑", key=f"del_{uid}"):
        delete_inventory(row["serial_no"])
        st.warning("Deleted")
        st.rerun()

st.divider()


# ----------------------------
# Footer
# ----------------------------
st.caption("Inventory Management System • Dashboard")