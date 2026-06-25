import sqlite3
import pytest
from unittest.mock import patch

@pytest.fixture
def test_db():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT,
        model TEXT,
        serial_no TEXT,
        item_category TEXT,
        quantity INTEGER,
        warranty_status TEXT,
        status TEXT,
        hand_over_to TEXT,
        issue_date TEXT,
        received_from TEXT,
        return_date TEXT,
        note TEXT,
        status_2 TEXT
    )
    """)

    conn.commit()

    with patch("inventory.get_connection", return_value=conn):
        yield conn

    conn.close()