import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import get_connection

st.set_page_config(
    page_title="Inventory Dashboard",
    layout="wide"
)

st.title("📊 IT Asset Management Dashboard")

# ==================================
# DATABASE FUNCTIONS
# ==================================

def fetch_inventory():
    conn = get_connection()

    query = """
        SELECT *
        FROM inventory
        ORDER BY id DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df


def fetch_employees():
    conn = get_connection()

    query = """
        SELECT *
        FROM employees
        ORDER BY id DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ==================================
# LOAD DATA
# ==================================

inventory_df = fetch_inventory()
employee_df = fetch_employees()

if inventory_df.empty:
    st.warning("No inventory records found.")
    st.stop()

inventory_df.columns = (
    inventory_df.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

employee_df.columns = (
    employee_df.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

inventory_df["status"] = inventory_df["status"].fillna("Unknown")
inventory_df["brand"] = inventory_df["brand"].fillna("Unknown")
inventory_df["item_category"] = inventory_df["item_category"].fillna("Unknown")

# ==================================
# FILTERS
# ==================================

st.subheader("🔍 Dashboard Filters")

f1, f2, f3 = st.columns(3)

brand_filter = f1.selectbox(
    "Brand",
    ["All"] + sorted(inventory_df["brand"].dropna().unique().tolist())
)

status_filter = f2.selectbox(
    "Status",
    ["All"] + sorted(inventory_df["status"].dropna().unique().tolist())
)

category_filter = f3.selectbox(
    "Category",
    ["All"] + sorted(inventory_df["item_category"].dropna().unique().tolist())
)

filtered_df = inventory_df.copy()

if brand_filter != "All":
    filtered_df = filtered_df[filtered_df["brand"] == brand_filter]

if status_filter != "All":
    filtered_df = filtered_df[filtered_df["status"] == status_filter]

if category_filter != "All":
    filtered_df = filtered_df[filtered_df["item_category"] == category_filter]

# ==================================
# KPI SECTION
# ==================================

total_assets = len(filtered_df)

issued_assets = len(filtered_df[filtered_df["status"] == "Issued"])
available_assets = len(filtered_df[filtered_df["status"] == "In-Inventory"])
damaged_assets = len(filtered_df[filtered_df["status"] == "Damaged"])

total_employees = len(employee_df)
active_employees = len(employee_df[employee_df["status"] == "Active"])

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("📦 Assets", total_assets)
c2.metric("🟢 Available", available_assets)
c3.metric("🔵 Issued", issued_assets)
c4.metric("🔴 Damaged", damaged_assets)
c5.metric("👨‍💼 Employees", total_employees)
c6.metric("✅ Active", active_employees)

st.divider()

# ==================================
# STATUS + BRAND
# ==================================

left, right = st.columns(2)

with left:
    st.subheader("📦 Asset Status")

    status_counts = filtered_df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    fig_status = px.pie(
        status_counts,
        names="Status",
        values="Count",
        hole=0.45
    )

    st.plotly_chart(fig_status, use_container_width=True)


with right:
    st.subheader("🏷 Brand Distribution")

    brand_counts = filtered_df["brand"].value_counts().reset_index()
    brand_counts.columns = ["Brand", "Count"]

    fig_brand = px.bar(
        brand_counts,
        x="Brand",
        y="Count",
        color="Brand",
        text="Count"
    )

    st.plotly_chart(fig_brand, use_container_width=True)

# ==================================
# CATEGORY + WARRANTY
# ==================================

left, right = st.columns(2)

with left:
    st.subheader("📂 Asset Categories")

    cat_counts = filtered_df["item_category"].value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]

    fig_cat = px.bar(
        cat_counts,
        x="Category",
        y="Count",
        color="Category",
        text="Count"
    )

    st.plotly_chart(fig_cat, use_container_width=True)


with right:
    st.subheader("🛡 Warranty Overview")

    warranty_counts = (
        filtered_df["warranty_status"]
        .fillna("NA")
        .value_counts()
        .reset_index()
    )

    warranty_counts.columns = ["Warranty Status", "Count"]

    fig_warranty = px.pie(
        warranty_counts,
        names="Warranty Status",
        values="Count",
        hole=0.45
    )

    st.plotly_chart(fig_warranty, use_container_width=True)

st.divider()

# ==================================
# EMPLOYEE ASSET SUMMARY
# ==================================

st.subheader("👨‍💼 Employee Asset Summary")

issued_df = filtered_df[filtered_df["status"] == "Issued"]

if not issued_df.empty:

    emp_summary = (
        issued_df.groupby("hand_over_to")
        .size()
        .reset_index(name="Assets Assigned")
    )

    emp_summary.columns = ["Employee ID", "Assets Assigned"]

    emp_summary = emp_summary.merge(
        employee_df[["employee_id", "employee_name", "department"]],
        left_on="Employee ID",
        right_on="employee_id",
        how="left"
    )

    fig_emp = px.bar(
        emp_summary,
        x="employee_name",
        y="Assets Assigned",
        color="department",
        text="Assets Assigned"
    )

    st.plotly_chart(fig_emp, use_container_width=True)

    st.dataframe(
        emp_summary[["Employee ID", "employee_name", "department", "Assets Assigned"]],
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No issued assets found.")

st.divider()

# ==================================
# DEPARTMENT WISE ASSETS
# ==================================

st.subheader("🏢 Department Asset Distribution")

if not issued_df.empty:

    dept_df = issued_df.merge(
        employee_df,
        left_on="hand_over_to",
        right_on="employee_id",
        how="left"
    )

    dept_summary = dept_df.groupby("department").size().reset_index(name="Assets")

    fig_dept = px.bar(
        dept_summary,
        x="department",
        y="Assets",
        color="department",
        text="Assets"
    )

    st.plotly_chart(fig_dept, use_container_width=True)

st.divider()

# ==================================
# TOP ASSET HOLDERS
# ==================================

st.subheader("🏆 Top Asset Holders")

if not issued_df.empty:

    top_users = (
        issued_df.groupby("hand_over_to")
        .size()
        .reset_index(name="Assets")
        .sort_values("Assets", ascending=False)
    )

    top_users = top_users.merge(
        employee_df[["employee_id", "employee_name", "department"]],
        left_on="hand_over_to",
        right_on="employee_id",
        how="left"
    )

    st.dataframe(
        top_users[["employee_name", "department", "Assets"]],
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==================================
# RECENT INVENTORY
# ==================================

# st.subheader("🆕 Latest Assets")

# latest_assets = filtered_df.head(10)

# st.dataframe(
#     latest_assets[
#         ["brand", "model", "serial_no", "status", "hand_over_to", "created_at"]
#     ],
#     use_container_width=True,
#     hide_index=True
# )
st.subheader("🆕 Latest Assets")

latest_assets = filtered_df.head(10)

expected_cols = [
    "brand",
    "model",
    "serial_no",
    "status",
    "hand_over_to",
    "created_at"
]

# keep only columns that actually exist
available_cols = [col for col in expected_cols if col in latest_assets.columns]

st.dataframe(
    latest_assets[available_cols],
    use_container_width=True,
    hide_index=True
)
st.divider()

# ==================================
# FULL INVENTORY
# ==================================

st.subheader("📋 Inventory Records")

search = st.text_input("Search Inventory", placeholder="Type anything...")

display_df = filtered_df.copy()

if search:
    display_df = display_df[
        display_df.apply(
            lambda r: r.astype(str).str.contains(search, case=False, na=False).any(),
            axis=1
        )
    ]

st.dataframe(display_df, use_container_width=True, hide_index=True)

# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from db_connection import get_connection

# st.set_page_config(
#     page_title="Inventory Dashboard",
#     layout="wide"
# )

# st.title("📊 IT Asset Management Dashboard")

# # ==============================
# # DATABASE FUNCTIONS
# # ==============================

# def fetch_inventory():
#     conn = get_connection()
#     query = """
#         SELECT *
#         FROM inventory
#         ORDER BY id DESC
#     """
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df


# def fetch_employees():
#     conn = get_connection()
#     query = """
#         SELECT *
#         FROM employees
#         ORDER BY id DESC
#     """
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df


# # ==============================
# # LOAD DATA
# # ==============================

# inventory_df = fetch_inventory()
# employee_df = fetch_employees()

# if inventory_df.empty:
#     st.warning("No inventory records found.")
#     st.stop()

# # Normalize column names
# inventory_df.columns = inventory_df.columns.str.lower().str.strip().str.replace(" ", "_")
# employee_df.columns = employee_df.columns.str.lower().str.strip().str.replace(" ", "_")

# # Fill missing values safely
# inventory_df["status"] = inventory_df["status"].fillna("Unknown")
# inventory_df["brand"] = inventory_df["brand"].fillna("Unknown")
# inventory_df["item_category"] = inventory_df["item_category"].fillna("Unknown")

# # ==============================
# # FILTERS
# # ==============================

# st.subheader("🔍 Dashboard Filters")

# f1, f2, f3 = st.columns(3)

# brand_filter = f1.selectbox(
#     "Brand",
#     ["All"] + sorted(inventory_df["brand"].dropna().unique().tolist())
# )

# status_filter = f2.selectbox(
#     "Status",
#     ["All"] + sorted(inventory_df["status"].dropna().unique().tolist())
# )

# category_filter = f3.selectbox(
#     "Category",
#     ["All"] + sorted(inventory_df["item_category"].dropna().unique().tolist())
# )

# filtered_df = inventory_df.copy()

# if brand_filter != "All":
#     filtered_df = filtered_df[filtered_df["brand"] == brand_filter]

# if status_filter != "All":
#     filtered_df = filtered_df[filtered_df["status"] == status_filter]

# if category_filter != "All":
#     filtered_df = filtered_df[filtered_df["item_category"] == category_filter]


# # ==============================
# # KPI SECTION (FIXED LOGIC)
# # ==============================

# total_assets = len(inventory_df)
# issued_assets = len(inventory_df[inventory_df["status"] == "Issued"])
# available_assets = len(inventory_df[inventory_df["status"] == "In-Inventory"])
# damaged_assets = len(inventory_df[inventory_df["status"] == "Damaged"])

# total_employees = len(employee_df)
# active_employees = len(employee_df[employee_df["status"] == "Active"])

# unassigned_assets = inventory_df["hand_over_to"].isna().sum()

# c1, c2, c3, c4, c5, c6 = st.columns(6)

# c1.metric("📦 Assets", total_assets)
# c2.metric("🟢 Available", available_assets)
# c3.metric("🔵 Issued", issued_assets)
# c4.metric("🔴 Damaged", damaged_assets)
# c5.metric("👨‍💼 Employees", total_employees)
# c6.metric("⚪ Unassigned", unassigned_assets)

# st.divider()


# # ==============================
# # STATUS + BRAND
# # ==============================

# left, right = st.columns(2)

# with left:
#     st.subheader("📦 Asset Status")

#     status_counts = filtered_df["status"].value_counts().reset_index()
#     status_counts.columns = ["Status", "Count"]

#     fig_status = px.pie(status_counts, names="Status", values="Count", hole=0.45)
#     st.plotly_chart(fig_status, use_container_width=True)

# with right:
#     st.subheader("🏷 Brand Distribution")

#     brand_counts = filtered_df["brand"].value_counts().reset_index()
#     brand_counts.columns = ["Brand", "Count"]

#     fig_brand = px.bar(
#         brand_counts,
#         x="Brand",
#         y="Count",
#         color="Brand",
#         text="Count"
#     )

#     st.plotly_chart(fig_brand, use_container_width=True)


# # ==============================
# # CATEGORY + WARRANTY (SAFE)
# # ==============================

# left, right = st.columns(2)

# with left:
#     st.subheader("📂 Asset Categories")

#     cat_counts = filtered_df["item_category"].value_counts().reset_index()
#     cat_counts.columns = ["Category", "Count"]

#     fig_cat = px.bar(cat_counts, x="Category", y="Count", color="Category", text="Count")
#     st.plotly_chart(fig_cat, use_container_width=True)

# with right:
#     st.subheader("🛡 Warranty Overview")

#     if "warranty_status" in filtered_df.columns:
#         warranty_counts = (
#             filtered_df["warranty_status"]
#             .fillna("NA")
#             .value_counts()
#             .reset_index()
#         )
#         warranty_counts.columns = ["Warranty Status", "Count"]
#     else:
#         warranty_counts = pd.DataFrame({
#             "Warranty Status": ["NA"],
#             "Count": [0]
#         })

#     fig_warranty = px.pie(
#         warranty_counts,
#         names="Warranty Status",
#         values="Count",
#         hole=0.45
#     )

#     st.plotly_chart(fig_warranty, use_container_width=True)

# st.divider()


# # ==============================
# # EMPLOYEE ASSET SUMMARY
# # ==============================

# st.subheader("👨‍💼 Employee Asset Summary")

# issued_df = filtered_df[filtered_df["status"] == "Issued"]

# if not issued_df.empty:

#     emp_summary = (
#         issued_df.groupby("hand_over_to")
#         .size()
#         .reset_index(name="Assets Assigned")
#     )

#     emp_summary.columns = ["Employee ID", "Assets Assigned"]

#     emp_summary = emp_summary.merge(
#         employee_df[["employee_id", "employee_name", "department"]],
#         left_on="Employee ID",
#         right_on="employee_id",
#         how="left"
#     )

#     emp_summary["employee_name"] = emp_summary["employee_name"].fillna("Unassigned")
#     emp_summary["department"] = emp_summary["department"].fillna("Unknown")

#     fig_emp = px.bar(
#         emp_summary,
#         x="employee_name",
#         y="Assets Assigned",
#         color="department",
#         text="Assets Assigned"
#     )

#     st.plotly_chart(fig_emp, use_container_width=True)

#     st.dataframe(
#         emp_summary[["Employee ID", "employee_name", "department", "Assets Assigned"]],
#         use_container_width=True,
#         hide_index=True
#     )

# else:
#     st.info("No issued assets found.")

# st.divider()


# # ==============================
# # DEPARTMENT WISE ASSETS
# # ==============================

# st.subheader("🏢 Department Asset Distribution")

# if not issued_df.empty:

#     dept_df = issued_df.merge(
#         employee_df,
#         left_on="hand_over_to",
#         right_on="employee_id",
#         how="left"
#     )

#     dept_summary = dept_df.groupby("department").size().reset_index(name="Assets")

#     fig_dept = px.bar(dept_summary, x="department", y="Assets", color="department", text="Assets")
#     st.plotly_chart(fig_dept, use_container_width=True)

# st.divider()


# # ==============================
# # TOP ASSET HOLDERS
# # ==============================

# st.subheader("🏆 Top Asset Holders")

# if not issued_df.empty:

#     top_users = (
#         issued_df.groupby("hand_over_to")
#         .size()
#         .reset_index(name="Assets")
#         .sort_values("Assets", ascending=False)
#     )

#     top_users = top_users.merge(
#         employee_df[["employee_id", "employee_name", "department"]],
#         left_on="hand_over_to",
#         right_on="employee_id",
#         how="left"
#     )

#     st.dataframe(
#         top_users[["employee_name", "department", "Assets"]],
#         use_container_width=True,
#         hide_index=True
#     )

# st.divider()


# # ==============================
# # LATEST ASSETS (FIXED)
# # ==============================

# st.subheader("🆕 Latest Assets")

# latest_assets = filtered_df.head(10)

# expected_cols = [
#     "brand",
#     "model",
#     "serial_no",
#     "status",
#     "hand_over_to",
#     "created_at"
# ]

# available_cols = [c for c in expected_cols if c in latest_assets.columns]

# st.dataframe(
#     latest_assets[available_cols],
#     use_container_width=True,
#     hide_index=True
# )


# st.divider()


# # ==============================
# # FULL INVENTORY SEARCH
# # ==============================

# st.subheader("📋 Inventory Records")

# search = st.text_input("Search Inventory", placeholder="Type anything...")

# display_df = filtered_df.copy()

# if search:
#     display_df = display_df[
#         display_df.apply(
#             lambda r: r.astype(str).str.contains(search, case=False, na=False).any(),
#             axis=1
#         )
#     ]

# st.dataframe(display_df, use_container_width=True, hide_index=True)