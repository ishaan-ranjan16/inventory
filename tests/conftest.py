import sqlite3
import tempfile
import pytest
from unittest.mock import patch


@pytest.fixture
def test_db():

    temp_db = tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False
    )

    db_path = temp_db.name

    conn = sqlite3.connect(db_path)

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
    conn.close()

    def get_test_connection():
        return sqlite3.connect(db_path)

    with patch(
        "inventory_core.get_connection",
        side_effect=get_test_connection
    ):
        yield