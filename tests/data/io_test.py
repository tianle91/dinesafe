from sqlalchemy import Connection

from dinesafe.data.io import (
    add_new_establishment,
    add_new_inspections,
    get_all_establishments,
    get_establishment,
    get_inspections,
)
from dinesafe.data.types import Establishment
from tests.constants import ESTABLISHMENT, INSPECTION


def test_get_establishment(connection: Connection):
    establishment = get_establishment(
        conn=connection, establishment_id=ESTABLISHMENT.establishment_id
    )
    assert establishment is None, establishment
    # insert one and get one
    add_new_establishment(conn=connection, establishment=ESTABLISHMENT)
    establishment = get_establishment(
        conn=connection, establishment_id=ESTABLISHMENT.establishment_id
    )
    assert isinstance(establishment, Establishment), establishment


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
