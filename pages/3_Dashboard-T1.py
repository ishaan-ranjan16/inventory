# # import streamlit as st
# # import pandas as pd

# # st.set_page_config(
# #     page_title="Dashboard",
# #     layout="wide"
# # )

# # st.title("📊 Dashboard")

# # # =========================
# # # SAFETY CHECKS
# # # =========================
# # inventory = st.session_state.get("inventory", pd.DataFrame())
# # employees = st.session_state.get("employees", pd.DataFrame())
# # assignments = st.session_state.get("assign", pd.DataFrame())

# # # =========================
# # # METRICS CALCULATION
# # # =========================
# # total_assets = len(inventory)
# # total_employees = len(employees)

# # issued_assets = 0
# # available_assets = 0
# # damaged_assets = 0
# # returned_assets = 0

# # if not inventory.empty:
# #     issued_assets = len(inventory[inventory["Status"] == "Issued"])
# #     available_assets = len(inventory[inventory["Status"] == "In-Inventory"])
# #     damaged_assets = len(inventory[inventory["Status"] == "Damaged"])

# # if not assignments.empty:
# #     returned_assets = len(assignments[assignments["Status"] == "Returned"])

# # c1, c2, c3, c4 = st.columns(4)

# # c1.metric("Total Assets", total_assets)
# # c2.metric("Employees", total_employees)
# # c3.metric("Issued Assets", issued_assets)
# # c4.metric("Returned Assets", returned_assets)

# # st.divider()

# # # =========================
# # # ASSET STATUS BREAKDOWN
# # # =========================
# # st.subheader("📦 Asset Status")

# # col1, col2, col3 = st.columns(3)

# # col1.metric("Available", available_assets)
# # col2.metric("Issued", issued_assets)
# # col3.metric("Damaged", damaged_assets)
# # st.divider()

# # # EMPLOYEE - ASSET SUMMARY
# # # ===================
# # st.subheader("👨‍💼 Employee Wise Asset Summary")

# # if employees.empty or inventory.empty:
# #     st.info("No data available.")
# # else:

# #     summary = []

# #     for _, emp in employees.iterrows():

# #         emp_key = f"{emp['Employee ID']} - {emp['Employee Name']}"

# #         count = len(
# #             inventory[
# #                 inventory["Handover to"] == emp_key
# #             ]
# #         )

# #         summary.append({
# #             "Employee ID": emp["Employee ID"],
# #             "Employee Name": emp["Employee Name"],
# #             "Assets Assigned": count
# #         })

# #     st.dataframe(
# #         pd.DataFrame(summary),
# #         use_container_width=True,
# #         hide_index=True
# #     )
# # st.divider()


# # # Inventory
# # # =========================
# # st.subheader("🏬 Inventory Snapp.")

# # if inventory.empty:
# #     st.info("No inventory available.")
# # else:

# #     st.dataframe(
# #         inventory.sort_values(by="Status", ascending=True),
# #         use_container_width=True,
# #         hide_index=True
# #     )

# # import streamlit as st
# # import pandas as pd
# # from db_connection import get_connection

# # st.set_page_config(page_title="Dashboard", layout="wide")

# # st.title("📊 Inventory Dashboard")


# # def fetch_inventory():
# #     conn = get_connection()
# #     df = pd.read_sql("SELECT * FROM inventory ORDER BY id DESC", conn)
# #     conn.close()
# #     return df


# # df = fetch_inventory()

# # if df.empty:
# #     st.warning("No data available")
# #     st.stop()

# # # =====================
# # # METRICS
# # # =====================

# # total = len(df)
# # issued = len(df[df["status"] == "Issued"])
# # available = len(df[df["status"] == "In-Inventory"])
# # damaged = len(df[df["status"] == "Damaged"])

# # c1, c2, c3, c4 = st.columns(4)

# # c1.metric("Total Assets", total)
# # c2.metric("Issued", issued)
# # c3.metric("Available", available)
# # c4.metric("Damaged", damaged)

# # st.divider()

# # # =====================
# # # CHART
# # # =====================

# # st.subheader("📦 Status Overview")
# # st.bar_chart(df["status"].value_counts())

# # st.subheader("🏷 Brand Distribution")
# # st.bar_chart(df["brand"].value_counts())

# # st.subheader("📂 Category Distribution")
# # st.bar_chart(df["item_category"].value_counts())

# import streamlit as st
# import pandas as pd
# from db_connection import get_connection

# st.set_page_config(page_title="Dashboard", layout="wide")

# st.title("📊 Inventory Dashboard")


# # =====================
# # LOAD DATA SAFELY
# # =====================

# def fetch_inventory():
#     conn = get_connection()
#     df = pd.read_sql("SELECT * FROM inventory ORDER BY id DESC", conn)
#     conn.close()
#     return df


# df = fetch_inventory()

# # =====================
# # SAFETY CLEANUP (IMPORTANT FIX)
# # =====================

# if df.empty:
#     st.warning("No data available")
#     st.stop()

# # normalize column names
# df.columns = df.columns.str.lower()

# # fill nulls to avoid chart errors
# df["status"] = df["status"].fillna("Unknown")
# df["brand"] = df["brand"].fillna("Unknown")
# df["item_category"] = df["item_category"].fillna("Unknown")


# # =====================
# # METRICS
# # =====================

# total = len(df)
# issued = len(df[df["status"] == "Issued"])
# available = len(df[df["status"] == "In-Inventory"])
# damaged = len(df[df["status"] == "Damaged"])

# c1, c2, c3, c4 = st.columns(4)

# c1.metric("Total Assets", total)
# c2.metric("Issued", issued)
# c3.metric("Available", available)
# c4.metric("Damaged", damaged)

# st.divider()


# # =====================
# # STATUS CHART
# # =====================

# st.subheader("📦 Status Overview")

# status_counts = df["status"].value_counts()
# st.bar_chart(status_counts)


# # =====================
# # BRAND CHART (SAFE)
# # =====================

# st.subheader("🏷 Brand Distribution")

# brand_counts = df["brand"].value_counts()
# if not brand_counts.empty:
#     st.bar_chart(brand_counts)
# else:
#     st.info("No brand data available")


# # =====================
# # CATEGORY CHART (SAFE)
# # =====================

# st.subheader("📂 Category Distribution")

# cat_counts = df["item_category"].value_counts()
# if not cat_counts.empty:
#     st.bar_chart(cat_counts)
# else:
#     st.info("No category data available")


# # =====================
# # EMPLOYEE-WISE SUMMARY (ADDED FEATURE)
# # =====================

# st.subheader("👨‍💼 Employee Asset Summary")

# if "hand_over_to" in df.columns:

#     emp_summary = (
#         df.groupby("hand_over_to")
#         .size()
#         .reset_index(name="Assets Assigned")
#     )

#     emp_summary.columns = ["Employee ID", "Assets Assigned"]

#     st.dataframe(emp_summary, use_container_width=True, hide_index=True)

# else:
#     st.warning("Employee allocation data not found")


# **************************************************
#****************************************************

import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import get_connection

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("📊 Inventory Dashboard")

# =====================
# LOAD DATA SAFELY
# =====================

def fetch_inventory():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM inventory ORDER BY id DESC", conn)
    conn.close()
    return df

df = fetch_inventory()

# =====================
# SAFETY CLEANUP
# =====================

if df.empty:
    st.warning("No data available")
    st.stop()

df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

df["status"] = df["status"].fillna("Unknown")
df["brand"] = df["brand"].fillna("Unknown")
df["item_category"] = df["item_category"].fillna("Unknown")

# METRICS
# =====================

total = len(df)
issued = len(df[df["status"] == "Issued"])
available = len(df[df["status"] == "In-Inventory"])
damaged = len(df[df["status"] == "Damaged"])

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Assets", total)
c2.metric("Issued", issued)
c3.metric("Available", available)
c4.metric("Damaged", damaged)

st.divider()

# =====================
# STATUS CHART--(PLOTLY)
# =====================

st.subheader("📦 Status Overview")

status_counts = df["status"].value_counts().reset_index()
status_counts.columns = ["status", "count"]

fig_status = px.bar(
    status_counts,
    x="status",
    y="count",
    color="status",
    text="count",
    title="Assets by Status"
)

st.plotly_chart(fig_status, use_container_width=True)

# =====================
# BRAND CHART --(PLOTLY)
# =====================

st.subheader("🏷 Brand Distribution")

brand_counts = df["brand"].value_counts().reset_index()
brand_counts.columns = ["brand", "count"]

fig_brand = px.bar(
    brand_counts,
    x="brand",
    y="count",
    color="brand",
    text="count",
    title="Assets by Brand"
)

st.plotly_chart(fig_brand, use_container_width=True)

# =====================
# CATEGORY CHART --(PLOTLY)
# =====================

st.subheader("📂 Category Distribution")

cat_counts = df["item_category"].value_counts().reset_index()
cat_counts.columns = ["category", "count"]

fig_cat = px.bar(
    cat_counts,
    x="category",
    y="count",
    color="category",
    text="count",
    title="Assets by Category"
)

st.plotly_chart(fig_cat, use_container_width=True)

# =====================
# EMPLOYEE-WISE SUMMARY
# =====================

st.subheader("👨‍💼 Employee Asset Summary")

if "hand_over_to" in df.columns:

    emp_summary = (
        df.groupby("hand_over_to")
        .size()
        .reset_index(name="assets_assigned")
    )

    emp_summary.columns = ["Employee ID", "Assets Assigned"]

    fig_emp = px.bar(
        emp_summary,
        x="Employee ID",
        y="Assets Assigned",
        text="Assets Assigned",
        title="Assets Assigned per Employee"
    )

    st.plotly_chart(fig_emp, use_container_width=True)

    st.dataframe(emp_summary, use_container_width=True, hide_index=True)

else:
    st.warning("Employee allocation data not found")
