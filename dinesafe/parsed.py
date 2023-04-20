import xmltodict

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Dict
from dinesafe.constants import YMD_FORMAT

import logging

logger = logging.getLogger(__name__)


@dataclass
class Infraction:
    severity: str
    deficiency: str
    action: str
    conviction_date: Optional[date] = None
    court_outcome: Optional[str] = None
    amount_fined: Optional[float] = None


@dataclass
class Inspection:
    status: str
    date: date
    infraction: List[Infraction]


@dataclass
class Establishment:
    id: str
    name: str
    type: str
    address: str
    latitude: float
    longitude: float
    status: str
    inspections: Dict[date, List[Inspection]]
    yelp_biz_result: Optional[dict] = None


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
        infraction=[get_infraction(d) for d in infraction_l],
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
