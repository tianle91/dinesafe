import logging
from typing import Dict, List, Optional

from sqlalchemy import Connection

from dinesafe.data.db.io import (
    add_new_establishment,
    add_new_inspections,
    get_all_establishments,
    get_all_latest_inspections,
)
from dinesafe.data.db.types import Inspection
from dinesafe.data.dinesafeto.convert import (
    convert_dinesafeto_establishment,
    convert_dinesafeto_inspection,
)
from dinesafe.data.dinesafeto.parsed import (
    download_dinesafeto,
    get_parsed_dinesafetoestablishments,
)

logger = logging.getLogger(__name__)


def refresh_dinesafeto_and_update_db(
    conn: Connection, path_to_xml: Optional[str] = None
):
    if path_to_xml is None:
        path_to_xml = download_dinesafeto()

    dinesafetoestablishments = get_parsed_dinesafetoestablishments(
        path_to_xml=path_to_xml
    )

    existing_establishment_ids = [
        establishment.establishment_id
        for establishment in get_all_establishments(conn=conn)
    ]
    latest_inspections_by_establishment = {
        inspection.establishment_id: inspection
        for inspection in get_all_latest_inspections(conn=conn)
    }

    new_establishment_counts = 0
    new_inspection_counts = 0
    for dinesafetoestablishment in dinesafetoestablishments.values():
        establishment = convert_dinesafeto_establishment(
            dinesafeto_establishment=dinesafetoestablishment
        )
        inspections = convert_dinesafeto_inspection(
            dinesafeto_establishment=dinesafetoestablishment
        )
        if establishment.establishment_id not in existing_establishment_ids:
            logger.info(
                f"Adding new establishment: {establishment.name} id: {establishment.establishment_id}"
            )
            add_new_establishment(conn=conn, establishment=establishment)
            new_establishment_counts += 1

        if establishment.establishment_id not in latest_inspections_by_establishment:
            new_inspections = inspections
        else:
            new_inspections = [
                inspection
                for inspection in inspections
                if inspection.timestamp
                > latest_inspections_by_establishment[
                    establishment.establishment_id
                ].timestamp
            ]

        # inspections may have duplicates
        new_inspections_by_id: Dict[str, List[Inspection]] = {}
        for inspection in new_inspections:
            new_inspections_by_id[inspection.inspection_id] = new_inspections_by_id.get(
                inspection.inspection_id, []
            ) + [inspection]
        # let's just pick the first one since the id is a content hash
        new_inspections = [new_inspections_by_id[k][0] for k in new_inspections_by_id]

        if len(new_inspections) > 0:
            logger.info(
                f"Adding {len(new_inspections)} new inspections for establishment id {establishment.establishment_id}: "
                + ", ".join(
                    sorted([inspection.inspection_id for inspection in new_inspections])
                )
            )
            add_new_inspections(conn=conn, inspections=new_inspections)
            new_inspection_counts += len(new_inspections)

    conn.commit()
    return (new_establishment_counts, new_inspection_counts)
