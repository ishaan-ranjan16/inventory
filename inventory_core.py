# inventory_core.py

import pandas as pd
import io

from datetime import date, datetime
from db_connection import get_connection

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet


def safe_date(val):
    if val is None or (isinstance(val, str) and val.strip() == ""):
        return date.today()

    if isinstance(val, str):
        try:
            return datetime.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            return date.today()

    return val if pd.notna(val) else date.today()


def fetch_inventory():
    columns = [
        "id", "brand", "model", "serial_no", "item_category",
        "quantity", "warranty_status", "status",
        "hand_over_to", "issue_date", "received_from",
        "return_date", "note", "status_2"
    ]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, brand, model, serial_no, item_category,
               quantity, warranty_status, status,
               hand_over_to, issue_date, received_from,
               return_date, note, status_2
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

    cur.execute("""
        INSERT INTO inventory (
            brand, model, serial_no, item_category,
            warranty_status, quantity, status,
            hand_over_to, issue_date, received_from,
            return_date, note, status_2
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    cur.close()
    conn.close()


def delete_inventory(record_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM inventory WHERE id=?",
        (record_id,)
    )

    conn.commit()
    cur.close()
    conn.close()


def update_inventory(values):
    conn = get_connection()
    cur = conn.cursor()

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
    """, values)

    conn.commit()
    cur.close()
    conn.close()


def generate_inventory_excel(df):
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Inventory"
        )

    buffer.seek(0)
    return buffer.getvalue()


def generate_inventory_pdf(df):
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

    elements = [
        Paragraph("Inventory Report", styles["Title"]),
        Spacer(1, 10)
    ]

    table_data = [list(df.columns)]

    for _, row in df.iterrows():
        table_data.append(
            [str(v) for v in row]
        )

    table = Table(table_data)

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return buffer.getvalue()