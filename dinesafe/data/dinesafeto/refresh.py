import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy import Connection
from dinesafe.data.dinesafeto.types import Establishment as DSTOEstablishment
from dinesafe.data.dinesafeto.convert import (
    convert_dinesafeto_establishment,
    convert_dinesafeto_inspection,
)
from dinesafe.data.types import Establishment, Inspection
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


def update_establishment_and_inspections(
    conn: Connection, dsto_estab: DSTOEstablishment
) -> Tuple[Establishment, Inspection]:
    # add new establishment if needed
    establishment = convert_dinesafeto_establishment(dsto_estab=dsto_estab)
    existing_estab = get_establishment(
        conn=conn, establishment_id=establishment.establishment_id
    )
    if existing_estab is None:
        logger.info(
            f"Adding new establishment: {establishment.name} id: {establishment.establishment_id}"
        )
        add_new_establishment(conn=conn, establishment=establishment, raise_error=False)

    # add new inspections if needed
    inspections = convert_dinesafeto_inspection(dsto_estab=dsto_estab)
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
        add_new_inspections(conn=conn, inspections=new_inspections, raise_error=False)

    # commit after potentially max of 2 executions
    conn.commit()
    return establishment, new_inspections


def refresh_dinesafeto_and_update_db(
    conn: Connection, path_to_xml: Optional[str] = None
) -> Tuple[List[Establishment], List[Inspection]]:
    if path_to_xml is None:
        path_to_xml = download_dinesafeto()

    # path_to_xml looks like {now_ts}.xml
    downloaded_ts = float(Path(path_to_xml).stem)
    dsto_estabs = get_parsed_dinesafetoestablishments(
        path_to_xml=path_to_xml,
        updated_timestamp=downloaded_ts,
    )
    establishments = []
    all_new_inspections = []
    for dsto_estab in dsto_estabs.values():
        establishment, new_inspections = update_establishment_and_inspections(
            conn=conn, dsto_estab=dsto_estab
        )
        establishments.append(establishment)
        all_new_inspections.extend(new_inspections)

    return (establishments, all_new_inspections)
