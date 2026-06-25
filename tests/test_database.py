from tests.inventory_core import (
    insert_inventory,
    fetch_inventory,
    delete_inventory,
)


def test_insert_inventory(test_db):

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

    assert len(df) == 1
    assert df.iloc[0]["brand"] == "Dell"


def test_delete_inventory(test_db):

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

    delete_inventory(row_id)

    df2 = fetch_inventory()

    assert len(df2) == 0