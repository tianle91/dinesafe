from typing import Dict

from sqlalchemy import text

from dinesafe.data.db.engine import get_inmemory_engine
from dinesafe.data.db.io import (
    add_new_establishment,
    add_new_inspections,
    create_establishment_table_if_not_exists,
    create_inspection_table_if_not_exists,
    get_all_establishments,
    get_all_latest_inspections,
    get_inspections,
    get_new_inspections,
)
from dinesafe.data.db.types import Establishment, Inspection
from dinesafe.data.dinesafeto.convert import (
    convert_dinesafeto_establishment,
    convert_dinesafeto_inspection,
)

ESTABLISHMENT_ID = "0"

ESTABLISHMENT = Establishment(
    establishment_id=ESTABLISHMENT_ID,
    name="establishment_0",
    address="address_1",
    latitude=0.0,
    longitude=0.0,
)

INSPECTION = Inspection(
    inspection_id="1",
    establishment_id=ESTABLISHMENT_ID,
    is_pass=True,
    timestamp=0,
)


def test_create_establishment_table_if_not_exists():
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        create_establishment_table_if_not_exists(conn=conn)


def test_create_inspection_table_if_not_exists():
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        create_inspection_table_if_not_exists(conn=conn)


def test_get_all_establishments():
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        create_establishment_table_if_not_exists(conn=conn)
        # nothing in db prior to inserting
        db_establishments = get_all_establishments(conn=conn)
        assert len(db_establishments) == 0, db_establishments


def test_add_new_establishment():
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        create_establishment_table_if_not_exists(conn=conn)
        # nothing in db prior to inserting
        db_establishments = get_all_establishments(conn=conn)
        assert len(db_establishments) == 0, db_establishments
        # insert one and get one
        add_new_establishment(conn=conn, establishment=ESTABLISHMENT)
        db_establishments = get_all_establishments(conn=conn)
        assert len(db_establishments) == 1, db_establishments


def test_add_new_inspections():
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        create_inspection_table_if_not_exists(conn=conn)
        create_establishment_table_if_not_exists(conn=conn)
        # nothing in db prior to inserting
        db_establishments = get_all_establishments(conn=conn)
        assert len(db_establishments) == 0, db_establishments
        db_inspections = get_inspections(conn=conn, establishment=ESTABLISHMENT)
        assert len(db_inspections) == 0, db_inspections

        # insert one and get one
        add_new_establishment(conn=conn, establishment=ESTABLISHMENT)
        add_new_inspections(conn=conn, inspections=[INSPECTION])
        db_establishments = get_all_establishments(conn=conn)
        assert len(db_establishments) == 1, db_establishments
        db_inspections = get_inspections(conn=conn, establishment=ESTABLISHMENT)
        assert len(db_inspections) == 1, db_inspections
