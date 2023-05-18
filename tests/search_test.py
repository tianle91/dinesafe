from sqlalchemy import Connection

from dinesafe.data.io import add_new_establishment
from dinesafe.search import get_relevant_establishment_ids
from tests.constants import (
    ESTABLISHMENT,
    ESTABLISHMENT_1,
    ESTABLISHMENT_ID,
    ESTABLISHMENT_ID_1,
    ESTABLISHMENT_NAME,
    ESTABLISHMENT_NAME_1,
)


def test_get_relevant_establishment_ids(connection: Connection):
    add_new_establishment(conn=connection, establishment=ESTABLISHMENT)
    add_new_establishment(conn=connection, establishment=ESTABLISHMENT_1)
    assert (
        get_relevant_establishment_ids(conn=connection, search_term=ESTABLISHMENT_NAME)[
            0
        ]
        == ESTABLISHMENT_ID
    )
    assert (
        get_relevant_establishment_ids(
            conn=connection, search_term=ESTABLISHMENT_NAME_1
        )[0]
        == ESTABLISHMENT_ID_1
    )
