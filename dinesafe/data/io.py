import logging
from dataclasses import asdict
from typing import List, Tuple, Optional

import pandas as pd
from sqlalchemy import Connection, CursorResult, Row, text

from dinesafe.data.types import Establishment, Inspection

logger = logging.getLogger(__name__)


def _parse_establishment_row(row: Row) -> Establishment:
    return Establishment(**row._asdict())


def _parse_inspection_row(row: Row) -> Inspection:
    return Inspection(**row._asdict())


def _execute_sql_from_file(
    conn: Connection, sql_query_file: str, **kwargs
) -> CursorResult:
    with open(sql_query_file) as f:
        sql_str = f.read()
    sql_str = sql_str.format(**kwargs) if len(kwargs) > 0 else sql_str
    return conn.execute(text(sql_str))


def create_establishment_table_if_not_exists(conn: Connection):
    _execute_sql_from_file(
        conn=conn, sql_query_file="dinesafe/data/sql/create_establishment.sql"
    )


def create_inspection_table_if_not_exists(conn: Connection):
    _execute_sql_from_file(
        conn=conn, sql_query_file="dinesafe/data/sql/create_inspection.sql"
    )


def get_establishment(
    conn: Connection, establishment_id: str
) -> Optional[Establishment]:
    result = _execute_sql_from_file(
        conn=conn,
        sql_query_file="dinesafe/data/sql/select_establishments.sql",
        establishment_id=establishment_id,
    )
    establishments = [_parse_establishment_row(row=row) for row in result]
    if len(establishments) > 1:
        raise KeyError(f"Duplicates found for establishment_id: {establishment_id}")
    elif len(establishments) == 0:
        return None
    else:
        return establishments[0]


def get_all_establishments(conn: Connection) -> List[Establishment]:
    result = conn.execute(text("SELECT * FROM establishment"))
    return [_parse_establishment_row(row=row) for row in result]


def get_total_num_inspections(conn: Connection) -> int:
    results = list(
        conn.execute(text("SELECT COUNT(*) AS num_inspections FROM inspection"))
    )
    if len(results) != 1:
        raise ValueError()
    return results[0].num_inspections


def get_inspections(conn: Connection, establishment: Establishment):
    result = _execute_sql_from_file(
        conn=conn,
        sql_query_file="dinesafe/data/sql/select_inspections.sql",
        establishment_id=establishment.establishment_id,
    )
    return [_parse_inspection_row(row=row) for row in result]


def add_new_establishment(
    conn: Connection, establishment: Establishment, raise_error: bool = True
):
    df = pd.DataFrame(data=[asdict(establishment)])
    try:
        df.to_sql(name="establishment", con=conn, if_exists="append", index=False)
    except Exception as e:
        logger.warning(
            f"Failed to add establishment (id: {establishment.establishment_id}): {establishment.name}"
        )
        logger.warning(df)
        logger.warning(e)
        if raise_error:
            raise e


def add_new_inspections(
    conn: Connection, inspections: List[Inspection], raise_error: bool = True
):
    df = pd.DataFrame(data=[asdict(inspection) for inspection in inspections])
    try:
        df.to_sql(name="inspection", con=conn, if_exists="append", index=False)
    except Exception as e:
        logger.warning(f"Failed to add {len(df)} inspections")
        logger.warning(df)
        logger.warning(e)
        if raise_error:
            raise e


def get_new_inspections(
    conn: Connection, establishment: Establishment, last_inspection_timestamp: float
) -> List[Inspection]:
    result = _execute_sql_from_file(
        conn=conn,
        sql_query_file="dinesafe/data/sql/select_new_inspections.sql",
        establishment_id=establishment.establishment_id,
        last_inspection_timestamp=last_inspection_timestamp,
    )
    return [_parse_inspection_row(row=row) for row in result]


def get_all_latest_inspections(conn: Connection):
    result = _execute_sql_from_file(
        conn=conn,
        sql_query_file="dinesafe/data/sql/select_all_latest_inspections.sql",
    )
    return [_parse_inspection_row(row=row) for row in result]


def get_latest(conn: Connection) -> List[Tuple[Establishment, Inspection]]:
    all_establishments = {
        establishment.establishment_id: establishment
        for establishment in get_all_establishments(conn=conn)
    }
    all_latest_inspections = {
        inspection.establishment_id: inspection
        for inspection in get_all_latest_inspections(conn=conn)
    }
    return [
        (all_establishments[k], all_latest_inspections[k])
        for k in all_latest_inspections
    ]
