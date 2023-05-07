from sqlalchemy import text

from dinesafe.data.db.engine import get_inmemory_engine
from dinesafe.data.db.io import add_new_establishment_if_not_exists, get_establishments
from dinesafe.data.dinesafeto.convert import (
    convert_dinesafeto_establishment,
    convert_dinesafeto_inspection,
)
from dinesafe.data.dinesafeto.parsed import get_parsed_establishments


def test_add_new_establishment_if_not_exists():
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        with open("dinesafe/data/db/sql/create_establishment.sql") as f:
            conn.execute(text(f.read()))
        print(get_establishments(conn=conn))

        dinesafeto_establishments = get_parsed_establishments(
            path_to_xml="tests/test_data/dinesafe/old.xml"
        )
        for dinesafeto_establishment in dinesafeto_establishments.values():
            establishment = convert_dinesafeto_establishment(
                dinesafeto_establishment=dinesafeto_establishment
            )
            add_new_establishment_if_not_exists(conn=conn, establishment=establishment)
            break
        print(get_establishments(conn=conn))
