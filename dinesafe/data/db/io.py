from datetime import date
from typing import Dict
from sqlalchemy import Connection, Row
from dinesafe.data.db.types import Establishment, Inspection
from typing import List
from sqlalchemy import text
import pandas as pd
import logging
from dataclasses import asdict

logger = logging.getLogger(__name__)


def parse_establishment_row(row: Row) -> Establishment:
    return Establishment(**row._asdict())


def parse_inspection_row(row: Row) -> Inspection:
    return Inspection(**row._asdict())


def add_new_establishment_if_not_exists(conn: Connection, establishment: Establishment):
    result = conn.execute(
        text(
            f"SELECT * FROM establishment WHERE establishment_id = {establishment.establishment_id}"
        )
    )
    if len(list(result)) == 0:
        logger.info(
            f"Adding establishment id: {establishment.establishment_id} since none was found"
        )
        pd.DataFrame(data=[asdict(establishment)]).to_sql(
            name="establishment", con=conn, if_exists="append", index=False
        )
        return True
    return False


def add_new_inspection_if_not_exists(conn: Connection, inspection: Inspection):
    pass


def get_establishments(conn: Connection) -> Dict[str, Establishment]:
    result = conn.execute(text("SELECT * FROM establishment"))
    return [parse_establishment_row(row=row) for row in result]


def get_inspections(conn: Connection, establishment: Establishment):
    pass


def get_new_inspections_since(conn: Connection, dt: date) -> List[Inspection]:
    pass
