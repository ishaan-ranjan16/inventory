import pandas as pd
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from inventory import safe_date

def test_safe_date_with_valid_date():
    d = date(2025, 1, 1)
    assert safe_date(d) == d

def test_safe_date_with_null():
    result = safe_date(pd.NaT)
    assert isinstance(result, date)