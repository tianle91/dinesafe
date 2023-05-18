import hashlib
import json
from typing import List

from dinesafe.data.dinesafeto.types import Establishment as DSTOEstablishment
from dinesafe.data.types import Establishment, Inspection


def convert_dinesafeto_establishment(dsto_estab: DSTOEstablishment) -> Establishment:
    extras_dict = {
        "type": dsto_estab.type,
        "status": dsto_estab.status,
    }
    return Establishment(
        establishment_id=dsto_estab.external_id,
        name=dsto_estab.name,
        address=dsto_estab.address,
        latitude=dsto_estab.latitude,
        longitude=dsto_estab.longitude,
        updated_timestamp=dsto_estab.updated_timestamp,
        details_json=json.dumps(extras_dict),
    )


def get_sha256_hash(s: str) -> str:
    m = hashlib.sha256()
    m.update(s.encode())
    return m.hexdigest()


def convert_dinesafeto_inspection(dsto_estab: DSTOEstablishment) -> List[Inspection]:
    inspections = []
    for dinesafeto_inspections in dsto_estab.inspections.values():
        for dinesafeto_inspection in dinesafeto_inspections:
            extras_dict = {
                "infractions": [
                    str(infraction) for infraction in dinesafeto_inspection.infractions
                ]
            }
            inspection = Inspection(
                inspection_id=get_sha256_hash(str(dinesafeto_inspection)),
                establishment_id=dsto_estab.external_id,
                is_pass=dinesafeto_inspection.status.lower() == "pass",
                timestamp=dinesafeto_inspection.date.timestamp(),
                updated_timestamp=dsto_estab.updated_timestamp,
                details_json=json.dumps(extras_dict),
            )
            inspections.append(inspection)
    return inspections
