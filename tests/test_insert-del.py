from unittest.mock import MagicMock, patch
from inventory import insert_inventory, delete_inventory

@patch("inventory.get_connection")
def test_insert_inventory(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.cursor.return_value = mock_cursor
    
    sample_data = (
        "HP", "ProBook", "SN123", "Laptop", "Under Warranty", 
        1, "In-Inventory", "None", None, "Vendor", None, "Note", "OK"
    )
    
    insert_inventory(sample_data)
    
    # Verify execution and commit
    mock_cursor.execute.assert_called_once()
    assert "INSERT INTO inventory" in mock_cursor.execute.call_args[0][0]
    assert mock_cursor.execute.call_args[0][1] == sample_data
    mock_conn.return_value.commit.assert_called_once()

@patch("inventory.get_connection")
def test_delete_inventory(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.cursor.return_value = mock_cursor
    
    delete_inventory("XYZ789")
    
    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM inventory WHERE serial_no=%s", ("XYZ789",)
    )
    mock_conn.return_value.commit.assert_called_once()