import io
import pandas as pd
from inventory import generate_inventory_excel

def test_excel_export_cleans_nulls():
    # DataFrame containing empty strings and missing entries
    dirty_df = pd.DataFrame({
        "brand": [""], "model": [None], "serial_no": ["SN1"], "item_category": ["PC"], 
        "quantity": [1], "warranty_status": [None], "status": ["Issued"], 
        "hand_over_to": [""], "issue_date": [None], "received_from": [""], 
        "return_date": [None], "note": [None], "status_2": [None]
    })
    
    excel_bytes = generate_inventory_excel(dirty_df)
    
    # Read it back using pandas to check content mutations
    processed_df = pd.read_excel(io.BytesIO(excel_bytes))
    
    # Check if empty values got correctly converted to '—'
    assert processed_df.iloc[0]["Brand"] == "—"
    assert processed_df.iloc[0]["Model"] == "—"
    assert processed_df.iloc[0]["Serial No"] == "SN1"