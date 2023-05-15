from sqlalchemy import Connection

from dinesafe.data.io import (
    add_new_establishment,
    add_new_inspections,
    get_all_establishments,
    get_inspections,
)
from dinesafe.data.types import Establishment, Inspection

ESTABLISHMENT_ID = "0"

ESTABLISHMENT = Establishment(
    establishment_id=ESTABLISHMENT_ID,
    name="establishment_0",
    address="address_1",
    latitude=0.0,
    longitude=0.0,
    updated_timestamp=0.0,
)

INSPECTION = Inspection(
    inspection_id="1",
    establishment_id=ESTABLISHMENT_ID,
    is_pass=True,
    timestamp=0,
    updated_timestamp=0.0,
)


def test_get_all_establishments(connection: Connection):
    # nothing in db prior to inserting
    db_establishments = get_all_establishments(conn=connection)
    assert len(db_establishments) == 0, db_establishments


def test_add_new_establishment(connection: Connection):
    # nothing in db prior to inserting
    db_establishments = get_all_establishments(conn=connection)
    assert len(db_establishments) == 0, db_establishments
    # insert one and get one
    add_new_establishment(conn=connection, establishment=ESTABLISHMENT)
    db_establishments = get_all_establishments(conn=connection)
    assert len(db_establishments) == 1, db_establishments


def test_add_new_inspections(connection: Connection):
    # nothing in db prior to inserting
    db_establishments = get_all_establishments(conn=connection)
    assert len(db_establishments) == 0, db_establishments
    db_inspections = get_inspections(conn=connection, establishment=ESTABLISHMENT)
    assert len(db_inspections) == 0, db_inspections

    # insert one and get one
    add_new_establishment(conn=connection, establishment=ESTABLISHMENT)
    add_new_inspections(conn=connection, inspections=[INSPECTION])
    db_establishments = get_all_establishments(conn=connection)
    assert len(db_establishments) == 1, db_establishments
    db_inspections = get_inspections(conn=connection, establishment=ESTABLISHMENT)
    assert len(db_inspections) == 1, db_inspections
