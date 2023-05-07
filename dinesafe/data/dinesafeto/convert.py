from dinesafe.data.dinesafeto.types import DinesafeTOEstablishment
from dinesafe.data.db.types import Establishment, Inspection
from dataclasses import asdict
import json
from typing import List


def convert_dinesafeto_establishment(
    dinesafeto_establishment: DinesafeTOEstablishment,
) -> Establishment:
    extras_dict = {
        "type": dinesafeto_establishment.type,
        "status": dinesafeto_establishment.status,
    }
    return Establishment(
        establishment_id=dinesafeto_establishment.id,
        name=dinesafeto_establishment.name,
        address=dinesafeto_establishment.address,
        latitude=dinesafeto_establishment.latitude,
        longitude=dinesafeto_establishment.longitude,
        details_json=json.dumps(extras_dict),
    )


def convert_dinesafeto_inspection(
    dinesafeto_establishment: DinesafeTOEstablishment,
) -> List[Inspection]:
    inspections = []
    for dinesafeto_inspections in dinesafeto_establishment.inspections.values():
        for dinesafeto_inspection in dinesafeto_inspections:
            extras_dict = {
                "inspections": [asdict(inspection) for inspection in inspections]
            }
            inspection = Inspection(
                inspection_id=str(hash(asdict(dinesafeto_inspection))),
                establishment_id=dinesafeto_establishment.id,
                is_pass=dinesafeto_inspection.status.lower() == "pass",
                date=dinesafeto_inspection.date,
                details_json=json.dumps(extras_dict),
            )
            inspections.append(inspection)
    return inspections
