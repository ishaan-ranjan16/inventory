import pandas as pd
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

@patch("inventory.fetch_inventory")
def test_search_filter_ui(mock_fetch):
    """Verifies that typing into the search bar works smoothly and filters data without runtime errors."""
    # 1. Mock a clean database row layout response
    mock_fetch.return_value = pd.DataFrame([{
        "id": 1, "brand": "Dell", "model": "Latitude", "serial_no": "123",
        "item_category": "Laptop", "quantity": 1, "warranty_status": "Yes",
        "status": "Issued", "hand_over_to": "Alex", "issue_date": None,
        "received_from": "Main", "return_date": None, "note": "", "status_2": ""
    }])
    
    # 2. Boot up the headless AppTest script framework
    app = AppTest.from_file("inventory.py").run()
    
    # 3. Target the search text box explicitly by its session key layout identifier
    search_input = app.get("text_input", key="search_box")
    assert len(search_input) > 0, "Could not find the inventory search box component!"
    
    # 4. Simulate typing a non-matching query terms string to trigger re-evaluation
    search_input[0].input("Apple").run()
    
    # 5. Core Assertions
    # Verify the layout engine finished execution without generating a red traceback error container block
    assert len(app.exception) == 0, f"Search component crashed with exception trace: {app.exception}"