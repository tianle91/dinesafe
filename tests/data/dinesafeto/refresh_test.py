import pandas as pd

from dinesafe.data.db.engine import get_inmemory_engine
from dinesafe.data.db.io import (create_establishment_table_if_not_exists,
                                 create_inspection_table_if_not_exists,
                                 get_all_establishments,
                                 get_total_num_inspections)
from dinesafe.data.dinesafeto.refresh import refresh_dinesafeto_and_update_db


def test_refresh_dinesafeto_and_update_db():
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        create_establishment_table_if_not_exists(conn=conn)
        create_inspection_table_if_not_exists(conn=conn)

    with engine.connect() as conn:
        refresh_dinesafeto_and_update_db(
            conn=conn, path_to_xml="tests/test_data/dinesafe/old.xml"
        )
        num_establishments = len(get_all_establishments(conn=conn))
        num_inspections = get_total_num_inspections(conn=conn)
        assert (num_establishments, num_inspections) == (2, 6)

        refresh_dinesafeto_and_update_db(
            conn=conn, path_to_xml="tests/test_data/dinesafe/new.xml"
        )
        num_establishments = len(get_all_establishments(conn=conn))
        num_inspections = get_total_num_inspections(conn=conn)
        assert (num_establishments, num_inspections) == (3, 7)
