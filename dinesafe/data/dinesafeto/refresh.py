import logging
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy import Connection

from dinesafe.data.dinesafeto.convert import (
    convert_dinesafeto_establishment,
    convert_dinesafeto_inspection,
)
from dinesafe.data.dinesafeto.parsed import (
    download_dinesafeto,
    get_parsed_dinesafetoestablishments,
)
from dinesafe.data.io import (
    add_new_establishment,
    add_new_inspections,
    get_all_establishments,
    get_inspections,
    get_establishment,
)

logger = logging.getLogger(__name__)


def refresh_dinesafeto_and_update_db(
    conn: Connection, path_to_xml: Optional[str] = None
):
    if path_to_xml is None:
        path_to_xml = download_dinesafeto()

    # path_to_xml looks like {now_ts}.xml
    downloaded_ts = float(Path(path_to_xml).stem)
    dinesafetoestablishments = get_parsed_dinesafetoestablishments(
        path_to_xml=path_to_xml,
        updated_timestamp=downloaded_ts,
    )

    new_establishment_counts = 0
    new_inspection_counts = 0
    for dinesafetoestablishment in dinesafetoestablishments.values():
        # add new establishment if needed
        establishment = convert_dinesafeto_establishment(
            dsto_estab=dinesafetoestablishment
        )
        if (
            get_establishment(
                conn=conn, establishment_id=establishment.establishment_id
            )
            is None
        ):
            logger.info(
                f"Adding new establishment: {establishment.name} id: {establishment.establishment_id}"
            )
            add_new_establishment(
                conn=conn, establishment=establishment, raise_error=False
            )
            new_establishment_counts += 1

        # add new inspections if needed
        inspections = convert_dinesafeto_inspection(dsto_estab=dinesafetoestablishment)
        existing_inspection_keys = set(
            inspection.inspection_id
            for inspection in get_inspections(conn=conn, establishment=establishment)
        )
        new_inspections = {
            inspection
            for inspection in inspections
            if inspection.inspection_id not in existing_inspection_keys
        }
        if len(new_inspections) > 0:
            logger.info(
                f"Adding {len(new_inspections)} new inspections for establishment id {establishment.establishment_id}: "
                + ", ".join(
                    sorted([inspection.inspection_id for inspection in new_inspections])
                )
            )
            add_new_inspections(
                conn=conn, inspections=new_inspections, raise_error=False
            )
            new_inspection_counts += len(new_inspections)

        # commit after potentially max of 2 executions
        conn.commit()

    return (new_establishment_counts, new_inspection_counts)
