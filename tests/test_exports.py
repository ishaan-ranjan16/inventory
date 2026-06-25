import pandas as pd

from tests.inventory_core import (
    generate_inventory_excel,
    generate_inventory_pdf,
)


def sample_df():
    return pd.DataFrame([
        {
            "brand": "Dell",
            "model": "Latitude",
            "serial_no": "ABC123",
        }
    ])


def test_excel_generation():
    result = generate_inventory_excel(sample_df())

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_pdf_generation():
    result = generate_inventory_pdf(sample_df())

    assert isinstance(result, bytes)
    assert result.startswith(b"%PDF")