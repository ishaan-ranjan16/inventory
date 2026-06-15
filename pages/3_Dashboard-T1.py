import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import get_connection

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("📊 Inventory Dashboard")

# =====================
# LOAD DATA FROM DB -
# =====================

def fetch_inventory():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM inventory ORDER BY id DESC", conn)
    conn.close()
    return df

df = fetch_inventory()

# =====================
# SAFETY CLEANUP -
# =====================

if df.empty:
    st.warning("No data available")
    st.stop()

df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

df["status"] = df["status"].fillna("Unknown")
df["brand"] = df["brand"].fillna("Unknown")
df["item_category"] = df["item_category"].fillna("Unknown")

# =====================
# METRICS -
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