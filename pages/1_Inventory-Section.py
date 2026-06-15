import streamlit as st
import pandas as pd
from datetime import date
from db_connection import get_connection

st.set_page_config(page_title="Inventory Section", layout="wide")
st.title("🏬 Inventory Section")

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

# ==========================
# METRICS --
# ==========================
total = len(df)
issued = len(df[df["status"] == "Issued"]) if not df.empty else 0
available = len(df[df["status"] == "In-Inventory"]) if not df.empty else 0
damaged = len(df[df["status"] == "Damaged"]) if not df.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", total)
c2.metric("Issued", issued)
c3.metric("Available", available)
c4.metric("Damaged", damaged)

st.divider()

# ==========================
# ➕ ADD INVENTORY -
# ==========================
if st.button("➕ Add Inventory"):
    add_inventory_dialog()

st.divider()

# ==========================
# 📦 INVENTORY DETAILS--
# ==========================
st.subheader("📦 Inventory Details")

search1 = st.text_input("Search Inventory Details")

details_df = df.copy()

if search1:
    details_df = details_df[
        details_df.apply(
            lambda r: r.astype(str).str.contains(search1, case=False, na=False).any(),
            axis=1
        )
    ]

st.dataframe(details_df, use_container_width=True, hide_index=True)

st.divider()

# ==========================
# 📋 INVENTORY LIST (with EDIT + DELETE)
# ==========================
st.subheader("📋 Inventory List")

search2 = st.text_input("Search Inventory List")

list_df = df.copy()

if search2:
    list_df = list_df[
        list_df.apply(
            lambda r: r.astype(str).str.contains(search2, case=False, na=False).any(),
            axis=1
        )
    ]


# Change the headers line - add a spacer column
h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h_gap, h15 = st.columns([1.5, 1.5, 1.5, 1.5, 1, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 2, 1.5, 0.5, 0.2, 0.5])
h1.markdown("**Brand**")
h2.markdown("**Model**")
h3.markdown("**Serial No**")
h4.markdown("**Category**")
h5.markdown("**Qty**")
h6.markdown("**Warranty**")
h7.markdown("**Status**")
h8.markdown("**Hand Over To**")
h9.markdown("**Issue Date**")
h10.markdown("**Received From**")
h11.markdown("**Return Date**")
h12.markdown("**Note**")
h13.markdown("**Status-2**")
h14.markdown("**Edit**")
# h_gap is intentionally left empty
h15.markdown("**Delete**")

st.divider()

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