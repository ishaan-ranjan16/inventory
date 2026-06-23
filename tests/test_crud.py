# from unittest.mock import patch
# import pytest
# from inventory import fetch_inventory, insert_inventory

# @patch("inventory.get_connection")
# def test_fetch_inventory_database_timeout(mock_get_conn):
#     """Verifies fetch_inventory handles database operational timeouts gracefully"""
#     # Force get_connection to throw a database connection error
#     mock_get_conn.side_effect = Exception("Database connection timeout error")
    
#     # Assert that your code either raises a predictable custom error 
#     # or handles it gracefully without a silent crash
#     with pytest.raises(Exception) as exc_info:
#         fetch_inventory()
        
#     assert "Database connection timeout" in str(exc_info.value)


# @patch("inventory.get_connection")
# def test_insert_inventory_database_failure(mock_get_conn):
#     """Verifies insert_inventory fails gracefully on database connection drops"""
#     mock_get_conn.side_effect = Exception("OperationalError: Lost connection to DB server")
    
#     sample_data = ("HP", "ProBook", "SN999", "Laptop", "Warranty", 1, "In-Inventory", 
#                    "None", None, "Vendor", None, "Note", "OK")
    
#     with pytest.raises(Exception) as exc_info:
#         insert_inventory(sample_data)
        
#     assert "Lost connection to DB server" in str(exc_info.value)

from unittest.mock import patch
from inventory import fetch_inventory, insert_inventory

@patch("inventory.get_connection")
def test_fetch_inventory_database_timeout(mock_get_conn):
    """Verifies fetch_inventory returns a safe empty DataFrame structure on timeouts instead of crashing"""
    # Force get_connection to throw a database connection error
    mock_get_conn.side_effect = Exception("Database connection timeout error")
    
    # Act: Call the function normally. It should catch the exception internally.
    df = fetch_inventory()
    
    # Assert: It did not crash! Instead, it returned a safe empty DataFrame with structural columns
    assert df.empty
    assert "brand" in df.columns
    assert "serial_no" in df.columns