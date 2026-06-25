# from tests.inventory_core import (
from inventory_core import (
    insert_inventory,
    update_inventory,
    fetch_inventory,
)


def test_update_inventory(test_db):

    insert_inventory((
        "Dell",
        "Latitude",
        "ABC123",
        "Laptop",
        "Active",
        1,
        "Issued",
        "John",
        None,
        "Vendor",
        None,
        "Testing",
        "Good"
    ))

    df = fetch_inventory()

    row_id = int(df.iloc[0]["id"])

    update_inventory((
        "HP",
        "EliteBook",
        "ABC123",
        "Laptop",
        "Expired",
        2,
        "Inventory",
        "Mike",
        None,
        "Vendor",
        None,
        "Updated",
        "Excellent",
        row_id
    ))

    updated = fetch_inventory()

    assert updated.iloc[0]["brand"] == "HP"
    assert updated.iloc[0]["quantity"] == 2