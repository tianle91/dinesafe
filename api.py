import logging
import os
from typing import Optional

import mysql.connector
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from mysql.connector import MySQLConnection

from dinesafe.data.dinesafeto.refresh import refresh_dinesafeto_and_update_db
from dinesafe.data.engine import get_local_engine, get_mysql_engine
from dinesafe.data.io import (
    create_establishment_table_if_not_exists,
    create_inspection_table_if_not_exists,
    get_all_establishments,
    get_establishment,
    get_inspections,
    get_latest,
    get_total_num_inspections,
)
from dinesafe.distances.geo import Coords
from dinesafe.search import get_relevant_establishment_ids

scheduler = BackgroundScheduler()
scheduler.start()

logger = logging.getLogger(__name__)
app = FastAPI(debug=True)

API_KEY = os.getenv("API_KEY", None)
MYSQL_URL = os.getenv("MYSQL_URL", None)
MYSQL_USER = os.getenv("MYSQL_USER", None)
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", None)

if API_KEY is None:
    raise ValueError("No API_KEY specified!")


def create_database_if_not_exists(mysql_conn: MySQLConnection, database_name: str):
    mycur = mysql_conn.cursor()
    mycur.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    mysql_conn.close()


if all([i is not None for i in (MYSQL_URL, MYSQL_USER, MYSQL_PASSWORD)]):
    myconn = mysql.connector.connect(
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_URL,
    )
    create_database_if_not_exists(mysql_conn=myconn, database_name="dinesafe")
    DB_ENGINE = get_mysql_engine(
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database="dinesafe",
        url=MYSQL_URL,
    )
else:
    logging.warning("Using sqlite")
    DB_ENGINE = get_local_engine()

with DB_ENGINE.connect() as conn:
    create_establishment_table_if_not_exists(conn=conn)
    create_inspection_table_if_not_exists(conn=conn)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # use token authentication


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden"
        )


@app.get("/")
def read_root():
    with DB_ENGINE.connect() as conn:
        establishments = get_all_establishments(conn=conn)
        num_inspections = get_total_num_inspections(conn=conn)
    return f"dinesafe api with {len(establishments)} establishments and {num_inspections} inspections."


@app.get("/latest", dependencies=[Depends(api_key_auth)])
def read_latest():
    with DB_ENGINE.connect() as conn:
        return get_latest(conn=conn)


@app.get("/search", dependencies=[Depends(api_key_auth)])
def read_search(
    search_term: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    accuracy: Optional[float] = None,
    limit: Optional[int] = 25,
    limit_inspections: Optional[int] = 5,
):
    coords = None
    if all([v is not None for v in (accuracy, latitude, longitude)]):
        coords = Coords(accuracy=accuracy, latitude=latitude, longitude=longitude)
    with DB_ENGINE.connect() as conn:
        relevant_establishment_ids = get_relevant_establishment_ids(
            conn=conn,
            coords=coords,
            search_term=search_term,
        )[:limit]
        # get sorted inspections
        result = []
        for establishment_id in relevant_establishment_ids:
            establishment = get_establishment(
                conn=conn, establishment_id=establishment_id
            )
            inspections = get_inspections(conn=conn, establishment=establishment)
            inspections = sorted(inspections, key=lambda v: v.timestamp, reverse=True)
            result.append((establishment, inspections[:limit_inspections]))
        return result


def _refresh_dinesafeto_and_update_db():
    with DB_ENGINE.connect() as conn:
        return refresh_dinesafeto_and_update_db(conn=conn)


@app.get("/refresh/{source_name}", dependencies=[Depends(api_key_auth)])
def refresh_source(source_name: str = "dinesafeto"):
    if source_name == "dinesafeto":
        scheduler.add_job(
            func=_refresh_dinesafeto_and_update_db,
            replace_existing=False,
            max_instances=1,
            id="_refresh_dinesafeto_and_update_db",
        )
    else:
        raise HTTPException(
            status_code=404, detail=f"source_name: {source_name} not found"
        )
