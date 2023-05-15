from typing import Dict

import pytest
from sqlalchemy import Connection

from dinesafe.data.dinesafeto.parsed import get_parsed_dinesafetoestablishments
from dinesafe.data.dinesafeto.types import Establishment as DSTOEstablishment
from dinesafe.data.engine import get_inmemory_engine
from dinesafe.data.io import (
    create_establishment_table_if_not_exists,
    create_inspection_table_if_not_exists,
)


@pytest.fixture(scope="session", autouse=True)
def old_parsed_dinesafetoestablishments() -> Dict[str, DSTOEstablishment]:
    return get_parsed_dinesafetoestablishments(
        path_to_xml="tests/test_data/dinesafe/1000.01.xml", updated_timestamp=1000.01
    )


@pytest.fixture(scope="function", autouse=True)
def connection() -> Connection:
    engine = get_inmemory_engine()
    with engine.connect() as conn:
        create_inspection_table_if_not_exists(conn=conn)
        create_establishment_table_if_not_exists(conn=conn)
        yield conn
