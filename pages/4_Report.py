# import streamlit as st
# import pandas as pd

# st.set_page_config(
#     page_title="Reports 📁",
#     layout="wide"
# )

# st.title("📁 Asset Reports")

# # =========================
# # LOAD DATA
# # =========================
# inventory_df = st.session_state.get("inventory", pd.DataFrame())
# employee_df = st.session_state.get("employees", pd.DataFrame())
# assignment_df = st.session_state.get("assignments", pd.DataFrame())

# # =========================
# # SUMMARY KPIs
# # =========================
# st.subheader("📊 Quick Summary")

# total_assets = len(inventory_df)
# total_employees = len(employee_df)

# issued = 0
# available = 0
# damaged = 0
# returned = 0

# if not inventory_df.empty:
#     issued = len(inventory_df[inventory_df["Status"] == "Issued"])
#     available = len(inventory_df[inventory_df["Status"] == "In-Inventory"])
#     damaged = len(inventory_df[inventory_df["Status"] == "Damaged"])

# if not assignment_df.empty:
#     returned = len(assignment_df[assignment_df["Status"] == "Returned"])

# c1, c2, c3, c4 = st.columns(4)

# c1.metric("Total Assets", total_assets)
# c2.metric("Total Employees", total_employees)
# c3.metric("Issued Assets", issued)
# c4.metric("Returned Assets", returned)

# st.divider()

# # =========================
# # INVENTORY REPORT
# # =========================
# st.subheader("📦 Inventory Report")

# if inventory_df.empty:
#     st.info("No inventory data.")
# else:

#     inventory_report = inventory_df[[
#         "Brand",
#         "Model",
#         "Serial No.",
#         "Item Category",
#         "Status",
#         "Handover to",
#         "Issue Date",
#         "Return Date"
#     ]]

#     st.dataframe(
#         inventory_report,
#         use_container_width=True,
#         hide_index=True
#     )

#     csv = inventory_report.to_csv(index=False)

#     st.download_button(
#         "⬇ Download Inventory Report",
#         data=csv,
#         file_name="inventory_report.csv",
#         mime="text/csv"
#     )

# st.divider()

# # =========================
# # EMPLOYEE REPORT
# # =========================
# st.subheader("👨‍💼 Employee Report")

# if employee_df.empty:
#     st.info("No employee data.")
# else:

#     emp_report = employee_df.copy()

#     # Add asset count per employee
#     asset_counts = []

#     for _, emp in employee_df.iterrows():

#         emp_key = f"{emp['Employee ID']} - {emp['Employee Name']}"

#         count = 0
#         if not inventory_df.empty:
#             count = len(
#                 inventory_df[
#                     inventory_df["Handover to"] == emp_key
#                 ]
#             )

#         asset_counts.append(count)

#     emp_report["Assets Assigned"] = asset_counts

#     st.dataframe(
#         emp_report,
#         use_container_width=True,
#         hide_index=True
#     )

#     csv = emp_report.to_csv(index=False)

#     st.download_button(
#         "⬇ Download Employee Report",
#         data=csv,
#         file_name="employee_report.csv",
#         mime="text/csv"
#     )

# st.divider()

# # INVENTORY_STATUS--
# # =========
# st.subheader("📊 Inventory Status Breakdown")

# if not inventory_df.empty:

#     status_summary = inventory_df["Status"].value_counts().reset_index()
#     status_summary.columns = ["Status", "Count"]

#     st.dataframe(
#         status_summary,
#         use_container_width=True,
#         hide_index=True
#     )
    

# ************************
# ************************

# import streamlit as st
# import pandas as pd
# from db_connection import get_connection

# st.set_page_config(page_title="Reports", layout="wide")

# st.title("📑 Inventory Reports")


# def fetch_inventory():
#     conn = get_connection()
#     df = pd.read_sql("SELECT * FROM inventory", conn)
#     conn.close()
#     return df


# df = fetch_inventory()

# if df.empty:
#     st.warning("No data available")
#     st.stop()

# # =====================
# # FILTERS
# # =====================

# col1, col2, col3 = st.columns(3)

# with col1:
#     status_filter = st.selectbox(
#         "Status",
#         ["All", "In-Inventory", "Issued", "Damaged"]
#     )

# with col2:
#     brand_filter = st.selectbox(
#         "Brand",
#         ["All"] + list(df["brand"].dropna().unique())
#     )

# with col3:
#     category_filter = st.selectbox(
#         "Category",
#         ["All"] + list(df["item_category"].dropna().unique())
#     )

# filtered = df.copy()

# if status_filter != "All":
#     filtered = filtered[filtered["status"] == status_filter]

# if brand_filter != "All":
#     filtered = filtered[filtered["brand"] == brand_filter]

# if category_filter != "All":
#     filtered = filtered[filtered["item_category"] == category_filter]

# st.write(f"📦 Records Found: {len(filtered)}")

# st.dataframe(filtered, use_container_width=True, hide_index=True)

# # =====================
# # DOWNLOADS
# # =====================

# csv = filtered.to_csv(index=False)

# st.download_button(
#     "⬇ Download CSV",
#     csv,
#     "inventory_report.csv",
#     "text/csv"
# )

# *************************

# import streamlit as st
# import pandas as pd
# from io import BytesIO
# from db_connection import get_connection

# from reportlab.lib import colors
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


# st.set_page_config(page_title="Reports", layout="wide")

# st.title("📑 Inventory Reports")


# # =====================
# # FETCH DATA
# # =====================
# def fetch_inventory():
#     conn = get_connection()
#     df = pd.read_sql("SELECT * FROM inventory", conn)
#     conn.close()
#     return df


# df = fetch_inventory()

# if df.empty:
#     st.warning("No data available")
#     st.stop()


# # =====================
# # FILTERS
# # =====================
# col1, col2, col3 = st.columns(3)

# with col1:
#     status_filter = st.selectbox(
#         "Status",
#         ["All", "In-Inventory", "Issued", "Damaged"]
#     )

# with col2:
#     brand_filter = st.selectbox(
#         "Brand",
#         ["All"] + list(df["brand"].dropna().unique())
#     )

# with col3:
#     category_filter = st.selectbox(
#         "Category",
#         ["All"] + list(df["item_category"].dropna().unique())
#     )


# filtered = df.copy()

# if status_filter != "All":
#     filtered = filtered[filtered["status"] == status_filter]

# if brand_filter != "All":
#     filtered = filtered[filtered["brand"] == brand_filter]

# if category_filter != "All":
#     filtered = filtered[filtered["item_category"] == category_filter]


# st.write(f"📦 Records Found: {len(filtered)}")

# st.dataframe(filtered, use_container_width=True, hide_index=True)


# # =====================
# # DOWNLOAD CSV
# # =====================
# csv = filtered.to_csv(index=False)

# st.download_button(
#     "⬇ Download CSV",
#     csv,
#     file_name="inventory_report.csv",
#     mime="text/csv"
# )


# # =====================
# # DOWNLOAD PDF
# # =====================
# def generate_pdf(dataframe):
#     buffer = BytesIO()

#     doc = SimpleDocTemplate(buffer, pagesize=letter)

#     # Convert dataframe to table data
#     data = [dataframe.columns.tolist()] + dataframe.astype(str).values.tolist()

#     table = Table(data)

#     style = TableStyle([
#         ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
#         ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
#         ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#         ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
#         ("ALIGN", (0, 0), (-1, -1), "CENTER"),
#         ("FONTSIZE", (0, 0), (-1, -1), 8),
#         ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
#     ])

#     table.setStyle(style)

#     doc.build([table])
#     buffer.seek(0)
#     return buffer


# pdf_buffer = generate_pdf(filtered)

# st.download_button(
#     "⬇ Download PDF",
#     pdf_buffer,
#     file_name="inventory_report.pdf",
#     mime="application/pdf"
# )

# ********************
# ********************

import streamlit as st
import pandas as pd
from io import BytesIO
from db_connection import get_connection

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


st.set_page_config(page_title="Report", layout="wide")

st.title("📑 Inventory Report")


# =====================
# FETCH DATA
# =====================
def fetch_inventory():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM inventory", conn)
    conn.close()
    return df


df = fetch_inventory()

if df.empty:
    st.warning("No data available")
    st.stop()


# =====================
# FILTERS
# =====================
col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox(
        "Status",
        ["All", "In-Inventory", "Issued", "Damaged"]
    )

with col2:
    brand_filter = st.selectbox(
        "Brand",
        ["All"] + list(df["brand"].dropna().unique())
    )

with col3:
    category_filter = st.selectbox(
        "Category",
        ["All"] + list(df["item_category"].dropna().unique())
    )


filtered = df.copy()

if status_filter != "All":
    filtered = filtered[filtered["status"] == status_filter]

if brand_filter != "All":
    filtered = filtered[filtered["brand"] == brand_filter]

if category_filter != "All":
    filtered = filtered[filtered["item_category"] == category_filter]


st.write(f"📦 Records Found: {len(filtered)}")

st.dataframe(filtered, use_container_width=True, hide_index=True)


# =====================
# DOWNLOAD CSV
# =====================
csv = filtered.to_csv(index=False)

st.download_button(
    "⬇ Download CSV",
    csv,
    file_name="inventory_report.csv",
    mime="text/csv"
)


# =====================
# DOWNLOAD PDF (LANDSCAPE / ROTATED)
# =====================
def generate_pdf(dataframe):
    buffer = BytesIO()

    # 👇 LANDSCAPE (ROTATED PAGE)
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))

    data = [dataframe.columns.tolist()] + dataframe.astype(str).values.tolist()

    table = Table(data)

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])

    table.setStyle(style)

    doc.build([table])
    buffer.seek(0)
    return buffer


pdf_buffer = generate_pdf(filtered)

st.download_button(
    "⬇ Download PDF",
    pdf_buffer,
    file_name="inventory_report.pdf",
    mime="application/pdf"
)