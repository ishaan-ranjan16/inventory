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
# DOWNLOAD CSV -
# =====================
csv = filtered.to_csv(index=False)

st.download_button(
    "⬇ Download CSV",
    csv,
    file_name="inventory_report.csv",
    mime="text/csv"
)


# =====================
# DOWNLOAD PDF (LANDSCAPE / ROTATED) -
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
    buffer.seek(0);
    return buffer


pdf_buffer = generate_pdf(filtered)

st.download_button(
    "⬇ Download PDF",
    pdf_buffer,
    file_name="inventory_report.pdf",
    mime="application/pdf"
)