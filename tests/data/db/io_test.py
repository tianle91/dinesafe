from typing import Dict

from sqlalchemy import text

from dinesafe.data.db.engine import get_inmemory_engine
from dinesafe.data.db.io import (
    add_new_establishment_if_not_exists,
    add_new_inspection_if_not_exists,
    get_establishments,
    get_inspections,
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
        establishments = get_establishments(conn=conn)
        assert len(establishments) == 0, establishments

        for dinesafeto_establishment in old_parsed_establishments.values():
            establishment = convert_dinesafeto_establishment(
                dinesafeto_establishment=dinesafeto_establishment
            )
            add_new_establishment_if_not_exists(conn=conn, establishment=establishment)
            break
        establishments = get_establishments(conn=conn)
        assert len(establishments) == 1, establishments


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
            inspections = get_inspections(conn=conn, establishment=establishment)
            assert len(inspections) == 0, inspections

            inspections = convert_dinesafeto_inspection(
                dinesafeto_establishment=dinesafeto_establishment
            )
            for inspection in inspections:
                add_new_inspection_if_not_exists(conn=conn, inspection=inspection)
                break
            break

        inspections = get_inspections(conn=conn, establishment=establishment)
        assert len(inspections) == 1, inspections
