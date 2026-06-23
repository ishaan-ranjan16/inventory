from unittest.mock import MagicMock, patch
from inventory import fetch_inventory

@patch("inventory.get_connection")
def test_fetch_inventory(mock_conn):

    mock_cursor = MagicMock()

    mock_cursor.fetchall.return_value = [
        (1, "Dell", "Latitude")
    ]

    mock_cursor.description = [
        ("id",),
        ("brand",),
        ("model",)
    ]

    mock_conn.return_value.cursor.return_value = mock_cursor

    df = fetch_inventory()

    assert len(df) == 1
    assert df.iloc[0]["brand"] == "Dell"