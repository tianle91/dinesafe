import logging
from dataclasses import asdict
from datetime import date
from typing import Dict, List

import pandas as pd
from sqlalchemy import Connection, Row, text

from dinesafe.data.db.types import Establishment, Inspection

logger = logging.getLogger(__name__)


def parse_establishment_row(row: Row) -> Establishment:
    return Establishment(**row._asdict())


def parse_inspection_row(row: Row) -> Inspection:
    return Inspection(**row._asdict())


def add_new_establishment_if_not_exists(conn: Connection, establishment: Establishment):
    with open("dinesafe/data/db/sql/select_establishments.sql") as f:
        result = conn.execute(
            text(f.read().format(establishment_id=establishment.establishment_id))
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
    with open("dinesafe/data/db/sql/select_existing_inspections.sql") as f:
        result = conn.execute(
            text(
                f.read().format(
                    establishment_id=inspection.establishment_id,
                    inspection_id=inspection.inspection_id,
                )
            )
        )
    if len(list(result)) == 0:
        logger.info(
            f"Adding inspection_id id: {inspection.inspection_id} since none was found"
        )
        pd.DataFrame(data=[asdict(inspection)]).to_sql(
            name="inspection", con=conn, if_exists="append", index=False
        )
        return True
    return False


def get_establishments(conn: Connection) -> Dict[str, Establishment]:
    result = conn.execute(text("SELECT * FROM establishment"))
    return [parse_establishment_row(row=row) for row in result]


def get_inspections(conn: Connection, establishment: Establishment):
    with open("dinesafe/data/db/sql/select_inspections.sql") as f:
        result = conn.execute(
            text(f.read().format(establishment_id=establishment.establishment_id))
        )
    return [parse_inspection_row(row=row) for row in result]


def get_new_inspections(
    conn: Connection, establishment: Establishment, last_inspection_timestamp: float
) -> List[Inspection]:
    with open("dinesafe/data/db/sql/select_new_inspections.sql") as f:
        query = f.read().format(
            establishment_id=establishment.establishment_id,
            last_inspection_timestamp=last_inspection_timestamp,
        )
    print(query)
    result = conn.execute(text(query))
    return [parse_inspection_row(row=row) for row in result]
