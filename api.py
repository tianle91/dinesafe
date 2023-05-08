from fastapi import FastAPI, HTTPException
from dinesafe.data.db.engine import get_local_engine
from dinesafe.data.db.io import (
    create_establishment_table_if_not_exists,
    create_inspection_table_if_not_exists,
    get_latest,
    get_all_establishments,
    get_total_num_inspections,
)
from dinesafe.data.dinesafeto.refresh import refresh_dinesafeto_and_update_db


app = FastAPI()

DB_ENGINE = get_local_engine()

with DB_ENGINE.connect() as conn:
    create_establishment_table_if_not_exists(conn=conn)
    create_inspection_table_if_not_exists(conn=conn)


@app.get("/")
def read_root():
    with DB_ENGINE.connect() as conn:
        establishments = get_all_establishments(conn=conn)
        num_inspections = get_total_num_inspections(conn=conn)
    return f"dinesafe api with {len(establishments)} establishments and {num_inspections} inspections."


@app.get("/latest")
def read_latest():
    with DB_ENGINE.connect() as conn:
        return get_latest(conn=conn)


@app.get("/refresh/{source_name}")
def refresh_source(source_name: str = "dinesafeto"):
    refresh_fn = lambda x: (0, 0)
    if source_name == "dinesafeto":
        refresh_fn = refresh_dinesafeto_and_update_db
    else:
        raise HTTPException(
            status_code=404, detail=f"source_name: {source_name} not found"
        )
    with DB_ENGINE.connect() as conn:
        (
            new_establishment_counts,
            new_inspection_counts,
        ) = refresh_fn(conn=conn)
        return {
            "new_establishment_counts": new_establishment_counts,
            "new_inspection_counts": new_inspection_counts,
        }
