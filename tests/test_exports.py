import pandas as pd
from inventory import (
    generate_inventory_excel,
    generate_inventory_pdf,
)

def sample_df():
    return pd.DataFrame(
        [
            {
                "brand": "Dell",
                "model": "Latitude",
                "serial_no": "ABC123",
                "item_category": "Laptop",
                "quantity": 1,
                "warranty_status": "Active",
                "status": "Issued",
                "hand_over_to": "John",
                "issue_date": "2025-01-01",
                "received_from": "Vendor",
                "return_date": "",
                "note": "Testing",
                "status_2": "Good",
            }
        ]
    )


def test_excel_generation():
    excel_bytes = generate_inventory_excel(sample_df())

    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0


def test_pdf_generation():
    pdf_bytes = generate_inventory_pdf(sample_df())

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")