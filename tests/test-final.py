from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import pandas as pd

@patch("inventory.fetch_inventory")
@patch("inventory.insert_inventory")
def test_add_item_via_ui(mock_insert, mock_fetch):
    # 1. Mock base UI state response
    mock_fetch.return_value = pd.DataFrame([]) # Empty inventory to start
    
    # 2. Boot up the Streamlit test application instance
    app = AppTest.from_file("inventory.py").run()
    
    # 3. Simulate user interactions (Find inputs by key or type)
    # Note: Adjust names if you used explicit labels or custom keys in st.text_input
    if app.text_input:
        app.text_input[0].input("Asus").run()       # Brand field
        app.text_input[1].input("ROG Strix").run()  # Model field
        app.text_input[2].input("SN-ASUS-77").run() # Serial field
        
    # 4. Simulate clicking the save submit action button if it exists
    if app.button:
        # Assuming your submit form button is the first or targeted button
        app.button[0].click().run()
        
    # 5. Assertions: Ensure no runtime script execution errors popped up
    assert len(app.exception) == 0