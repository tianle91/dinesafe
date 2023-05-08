import logging
import os
import time
from datetime import datetime
from typing import Dict, Optional

import wget
import xmltodict

from dinesafe.constants import YMD_FORMAT
from dinesafe.data.dinesafeto.types import (DinesafeTOEstablishment,
                                            DinesafeTOInfraction,
                                            DinesafeTOInspection)

logger = logging.getLogger(__name__)

# alternative sources
# https://open.toronto.ca/dataset/dinesafe/
# https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/dinesafe
URL = "https://secure.toronto.ca/opendata/ds/od_xml/v2?format=xml&stream=n"


def download_dinesafeto(download_directory="data/dinesafe") -> Optional[str]:
    now_ts = time.time()
    download_fname = f"{now_ts}.xml"
    download_path = os.path.join(download_directory, download_fname)
    logger.info(f"Downloading to {download_path}")
    try:
        wget.download(URL, out=download_path)
        return download_path
    except Exception as e:
        logger.error(str(e))
    return None


def get_parsed_value(d, k):
    v = d[k]
    if v is None:
        return None
    if "DATE" in k:
        return datetime.strptime(v, YMD_FORMAT)
    if "AMOUNT" in k or "LATITUDE" in k or "LONGITUDE" in k:
        return float(v)
    return v


def get_infraction(d: dict) -> DinesafeTOInfraction:
    return DinesafeTOInfraction(
        severity=get_parsed_value(d, "SEVERITY"),
        deficiency=get_parsed_value(d, "DEFICIENCY"),
        action=get_parsed_value(d, "ACTION"),
        court_outcome=get_parsed_value(d, "COURT_OUTCOME"),
        amount_fined=get_parsed_value(d, "AMOUNT_FINED"),
    )


def get_inspection(d: dict) -> DinesafeTOInspection:
    # get list of dicts for infraction
    infraction_d_or_l = d.get("INFRACTION", [])
    if isinstance(infraction_d_or_l, dict):
        infraction_l = [infraction_d_or_l]
    else:
        infraction_l = infraction_d_or_l

    return DinesafeTOInspection(
        status=get_parsed_value(d, "STATUS"),
        date=get_parsed_value(d, "DATE"),
        infractions=[get_infraction(d) for d in infraction_l],
    )


def get_establishment(d: dict) -> DinesafeTOEstablishment:
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

    return DinesafeTOEstablishment(
        id=get_parsed_value(d, "ID"),
        name=get_parsed_value(d, "NAME"),
        type=get_parsed_value(d, "TYPE"),
        address=get_parsed_value(d, "ADDRESS"),
        latitude=get_parsed_value(d, "LATITUDE"),
        longitude=get_parsed_value(d, "LONGITUDE"),
        status=get_parsed_value(d, "STATUS"),
        inspections=inspections,
    )


def get_parsed_dinesafetoestablishments(
    path_to_xml: str,
) -> Dict[str, DinesafeTOEstablishment]:
    establishment_l = []
    with open(path_to_xml) as f:
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
