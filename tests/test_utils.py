from datetime import date
from inventory import safe_date

def test_safe_date_none():
    assert safe_date(None) == date.today()


def test_safe_date_empty():
    assert safe_date("") == date.today()


def test_safe_date_string():
    result = safe_date("2025-01-01")
    assert result.year == 2025
    assert result.month == 1
    assert result.day == 1


def test_safe_date_invalid():
    assert safe_date("abc") == date.today()