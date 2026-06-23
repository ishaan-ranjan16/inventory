# from unittest.mock import MagicMock, patch
# from inventory import update_inventory

# @patch("inventory.get_connection")
# def test_update_inventory(mock_conn):
#     # 1. Arrange: Setup our fake database connection and cursor
#     mock_cursor = MagicMock()
#     mock_conn.return_value.cursor.return_value = mock_cursor
    
#     # Define sample data to mimic user edits in the form
#     target_serial = "OLD-SN-999"
#     updated_values = (
#         "Lenovo",          # brand
#         "ThinkPad T14",    # model
#         "NEW-SN-111",      # serial_no (new/edited serial)
#         "Laptop",          # item_category
#         "Out of Warranty", # warranty_status
#         1,                 # quantity
#         "In-Inventory",    # status
#         "None",            # hand_over_to
#         None,              # issue_date
#         "IT Dept",         # received_from
#         None,              # return_date
#         "Updated note",    # note
#         "Backup",          # status_2
#         target_serial      # WHERE serial_no = %s
#     )
    
#     # 2. Act: Call the update function
#     update_inventory(target_serial, updated_values)

#     # 2. Act: Call the update function with just the single tuple parameter
#     # update_inventory(updated_values)
    
#     # 3. Assert: Verify the SQL was targeted correctly
#     mock_cursor.execute.assert_called_once()
    
#     # Extract the exact arguments sent to cursor.execute(sql, params)
#     called_sql, called_params = mock_cursor.execute.call_args[0]
    
#     # Verify it targeted the correct statement structure
#     assert "UPDATE inventory" in called_sql
#     assert "SET" in called_sql
#     assert "WHERE serial_no=%s" in called_sql
    
#     # Verify the tuple data perfectly matches what the database expected
#     assert called_params == updated_values
#     assert called_params[-1] == target_serial  # Ensure the target condition parameter is at the end
    
#     # Verify the database transaction was saved
#     mock_conn.return_value.commit.assert_called_once()

from datetime import date
from unittest.mock import MagicMock, patch
from inventory import update_inventory

@patch("inventory.get_connection")
def test_update_inventory_with_none_dates(mock_conn):
    """Verifies update succeeds when date fields are missing (None)"""
    # 1. Arrange
    mock_cursor = MagicMock()
    mock_conn.return_value.cursor.return_value = mock_cursor
    
    target_serial = "OLD-SN-999"
    updated_values = (
        "Lenovo",          # brand
        "ThinkPad T14",    # model
        "NEW-SN-111",      # serial_no
        "Laptop",          # item_category
        "Out of Warranty", # warranty_status
        1,                 # quantity
        "In-Inventory",    # status
        "None",            # hand_over_to
        None,              # issue_date (None fallback)
        "IT Dept",         # received_from
        None,              # return_date (None fallback)
        "Updated note",    # note
        "Backup",          # status_2
        target_serial      # WHERE serial_no = %s
    )
    
    # 2. Act
    update_inventory(updated_values)
    
    # 3. Assert
    mock_cursor.execute.assert_called_once()
    called_sql, called_params = mock_cursor.execute.call_args[0]
    
    assert "UPDATE inventory" in called_sql
    assert "WHERE serial_no=%s" in called_sql
    assert called_params == updated_values
    mock_conn.return_value.commit.assert_called_once()


@patch("inventory.get_connection")
def test_update_inventory_converts_date_objects(mock_conn):
    """Verifies that active Python date objects are correctly stringified for SQL"""
    # 1. Arrange
    mock_cursor = MagicMock()
    mock_conn.return_value.cursor.return_value = mock_cursor
    
    target_serial = "OLD-SN-999"
    updated_values = (
        "Lenovo",          # brand
        "ThinkPad T14",    # model
        "NEW-SN-111",      # serial_no
        "Laptop",          # item_category
        "Out of Warranty", # warranty_status
        1,                 # quantity
        "In-Inventory",    # status
        "None",            # hand_over_to
        date(2026, 4, 12), # issue_date object
        "IT Dept",         # received_from
        date(2028, 9, 30), # return_date object
        "Updated note",    # note
        "Backup",          # status_2
        target_serial      # WHERE serial_no = %s
    )
    
    # 2. Act
    update_inventory(updated_values)
    
    # 3. Assert
    mock_cursor.execute.assert_called_once()
    _, called_params = mock_cursor.execute.call_args[0]
    
    # The application code transforms date objects to 'YYYY-MM-DD' strings for SQL
    assert called_params[8] == "2026-04-12"
    assert called_params[10] == "2028-09-30"
    assert called_params[-1] == target_serial
    mock_conn.return_value.commit.assert_called_once()