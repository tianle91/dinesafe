from typing import Dict
import copy
from sqlalchemy import text

from dinesafe.data.db.engine import get_inmemory_engine
from dinesafe.data.db.io import (
    add_new_establishment_if_not_exists,
    add_new_inspection_if_not_exists,
    get_establishments,
    get_inspections,
    get_new_inspections,
)
from dinesafe.data.dinesafeto.convert import (
    convert_dinesafeto_establishment,
    convert_dinesafeto_inspection,
)
from dinesafe.data.dinesafeto.types import DinesafeTOEstablishment


def test_add_new_establishment_if_not_exists(
    old_parsed_establishments: Dict[str, DinesafeTOEstablishment]
):
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        with open("dinesafe/data/db/sql/create_establishment.sql") as f:
            conn.execute(text(f.read()))
        db_establishments = get_establishments(conn=conn)
        assert len(db_establishments) == 0, db_establishments

        for dinesafeto_establishment in old_parsed_establishments.values():
            establishment = convert_dinesafeto_establishment(
                dinesafeto_establishment=dinesafeto_establishment
            )
            add_new_establishment_if_not_exists(conn=conn, establishment=establishment)
            break
        db_establishments = get_establishments(conn=conn)
        assert len(db_establishments) == 1, db_establishments


def test_add_new_inspection_if_not_exists(
    old_parsed_establishments: Dict[str, DinesafeTOEstablishment]
):
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        with open("dinesafe/data/db/sql/create_inspection.sql") as f:
            conn.execute(text(f.read()))

        for dinesafeto_establishment in old_parsed_establishments.values():
            establishment = convert_dinesafeto_establishment(
                dinesafeto_establishment=dinesafeto_establishment
            )
            db_inspections = get_inspections(conn=conn, establishment=establishment)
            assert len(db_inspections) == 0, db_inspections

            inspections = convert_dinesafeto_inspection(
                dinesafeto_establishment=dinesafeto_establishment
            )
            for inspection in inspections:
                add_new_inspection_if_not_exists(conn=conn, inspection=inspection)
                break
            break

        db_inspections = get_inspections(conn=conn, establishment=establishment)
        assert len(db_inspections) == 1, db_inspections


def test_get_new_inspections(
    old_parsed_establishments: Dict[str, DinesafeTOEstablishment]
):
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        with open("dinesafe/data/db/sql/create_inspection.sql") as f:
            conn.execute(text(f.read()))

        for dinesafeto_establishment in old_parsed_establishments.values():
            establishment = convert_dinesafeto_establishment(
                dinesafeto_establishment=dinesafeto_establishment
            )
            db_inspections = get_inspections(conn=conn, establishment=establishment)
            assert len(db_inspections) == 0, db_inspections

            inspections = convert_dinesafeto_inspection(
                dinesafeto_establishment=dinesafeto_establishment
            )
            ts_to_number_of_inspections = {}
            for inspection in inspections:
                ts_to_number_of_inspections[inspection.timestamp] = (
                    ts_to_number_of_inspections.get(inspection.timestamp, 0) + 1
                )
            assert len(ts_to_number_of_inspections) > 0, ts_to_number_of_inspections

            for inspection in inspections:
                add_new_inspection_if_not_exists(conn=conn, inspection=inspection)
            break

        earliest_inspection_ts = min(ts_to_number_of_inspections.keys())
        total_inspection_counts = sum(ts_to_number_of_inspections.values())

        db_inspections = get_new_inspections(
            conn=conn,
            establishment=establishment,
            last_inspection_timestamp=earliest_inspection_ts,
        )
        assert (
            len(db_inspections)
            == total_inspection_counts
            - ts_to_number_of_inspections[earliest_inspection_ts]
        ), ts_to_number_of_inspections
