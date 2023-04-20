import xmltodict

from datetime import date, datetime
from typing import List, Dict
from dinesafe.constants import YMD_FORMAT
from dinesafe.types import Infraction, Establishment, Inspection
import logging

logger = logging.getLogger(__name__)


def get_parsed_value(d, k):
    v = d[k]
    if v is None:
        return None
    if "DATE" in k:
        return datetime.strptime(v, YMD_FORMAT)
    if "AMOUNT" in k or "LATITUDE" in k or "LONGITUDE" in k:
        return float(v)
    return v


def get_infraction(d: dict) -> Infraction:
    return Infraction(
        severity=get_parsed_value(d, "SEVERITY"),
        deficiency=get_parsed_value(d, "DEFICIENCY"),
        action=get_parsed_value(d, "ACTION"),
        court_outcome=get_parsed_value(d, "COURT_OUTCOME"),
        amount_fined=get_parsed_value(d, "AMOUNT_FINED"),
    )


def get_inspection(d: dict) -> Inspection:
    # get list of dicts for infraction
    infraction_d_or_l = d.get("INFRACTION", [])
    if isinstance(infraction_d_or_l, dict):
        infraction_l = [infraction_d_or_l]
    else:
        infraction_l = infraction_d_or_l

    return Inspection(
        status=get_parsed_value(d, "STATUS"),
        date=get_parsed_value(d, "DATE"),
        infractions=[get_infraction(d) for d in infraction_l],
    )


def get_establishment(d: dict) -> Establishment:
    # get list of dicts for inspection
    inspection_d_or_l = d.get("INSPECTION", [])
    if isinstance(inspection_d_or_l, dict):
        inspection_l = [inspection_d_or_l]
    else:
        inspection_l = inspection_d_or_l

    inspections = {}
    for inspection_d in inspection_l:
        inspection = get_inspection(inspection_d)
        inspections[inspection.date] = inspections.get(inspection.date, []) + [
            inspection
        ]

    return Establishment(
        id=get_parsed_value(d, "ID"),
        name=get_parsed_value(d, "NAME"),
        type=get_parsed_value(d, "TYPE"),
        address=get_parsed_value(d, "ADDRESS"),
        latitude=get_parsed_value(d, "LATITUDE"),
        longitude=get_parsed_value(d, "LONGITUDE"),
        status=get_parsed_value(d, "STATUS"),
        inspections=inspections,
    )


def get_parsed_establishments(p: str) -> Dict[str, Establishment]:
    establishment_l = []
    with open(p) as f:
        establishment_l = xmltodict.parse(f.read())["DINESAFE_DATA"]["ESTABLISHMENT"]
    establishments = {}
    for d in establishment_l:
        try:
            establishment = get_establishment(d)
        except Exception as e:
            logger.error(f"Failed to parse establishment: {d}")
            raise (e)

        if establishment.id in establishments:
            raise KeyError(
                f"Establishment {establishment.id} already in establishments: {establishments}"
            )
        establishments[establishment.id] = establishment
    return establishments


def get_new_establishments(
    new: Dict[str, Establishment],
    old: Dict[str, Establishment],
) -> Dict[str, Establishment]:
    return {k: new[k] for k in set(new.keys()) - set(old.keys())}


def get_new_inspections(
    new: Dict[str, Establishment],
    old: Dict[str, Establishment],
) -> Dict[str, Dict[date, List[Inspection]]]:
    out = {}
    for k in old:
        old_estab = old[k]
        if k not in new:
            logger.warning(f"Establishment: {k} not found in new!")
        else:
            new_estab = new[k]
            new_inspections = {}
            for dt in new_estab.inspections:
                new_inspections_dt = [
                    inspection
                    for inspection in new_estab.inspections[dt]
                    if inspection not in old_estab.inspections.get(dt, [])
                ]
                if len(new_inspections_dt) > 0:
                    new_inspections[dt] = new_inspections_dt
            if len(new_inspections) > 0:
                out[k] = new_inspections
    return out
