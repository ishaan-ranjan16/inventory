from streamlit.testing.v1 import AppTest
import pytest

@patch("inventory.fetch_inventory")
def test_search_filter_ui(mock_fetch):
    # Mock database back-end response for UI testing
    mock_fetch.return_value = pd.DataFrame([{
        "id": 1, "brand": "Dell", "model": "Latitude", "serial_no": "123",
        "item_category": "Laptop", "quantity": 1, "warranty_status": "Yes",
        "status": "Issued", "hand_over_to": "Alex", "issue_date": None,
        "received_from": "Main", "return_date": None, "note": "", "status_2": ""
    }])
    
    app = AppTest.from_file("inventory.py").run()
    
    # Find search input field and simulate a query that won't match
    search_input = app.text_input[0]
    search_input.input("Apple").run()
    
    # Ensure no exception was raised during run-time search filtering execution
    assert len(app.exception) == 0