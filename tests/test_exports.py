import pandas as pd
from inventory import (
    generate_inventory_excel,
    generate_inventory_pdf
)

def sample_df():
    return pd.DataFrame({
        "brand": ["Dell"],
        "model": ["Latitude"],
        "serial_no": ["ABC123"],
        "item_category": ["Laptop"],
        "quantity": [1],
        "warranty_status": ["Warranty"],
        "status": ["Issued"],
        "hand_over_to": ["John"],
        "issue_date": [None],
        "received_from": ["Vendor"],
        "return_date": [None],
        "note": ["Test"],
        "status_2": ["OK"]
    })

def test_excel_export():
    data = generate_inventory_excel(sample_df())
    assert isinstance(data, bytes)
    assert len(data) > 0

def test_pdf_export():
    data = generate_inventory_pdf(sample_df())
    assert isinstance(data, bytes)
    assert len(data) > 0