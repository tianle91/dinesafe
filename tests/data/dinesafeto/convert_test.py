from typing import Dict

from dinesafe.data.dinesafeto.convert import (
    convert_dinesafeto_establishment,
    convert_dinesafeto_inspection,
)
from dinesafe.data.dinesafeto.parsed import get_parsed_dinesafetoestablishments
from dinesafe.data.dinesafeto.types import DinesafeTOEstablishment


def test_convert_dinesafeto_establishment(
    old_parsed_dinesafetoestablishments: Dict[str, DinesafeTOEstablishment]
):
    for dinesafeto_establishment in old_parsed_dinesafetoestablishments.values():
        convert_dinesafeto_establishment(
            dinesafeto_establishment=dinesafeto_establishment
        )


def test_convert_dinesafeto_inspection(
    old_parsed_dinesafetoestablishments: Dict[str, DinesafeTOEstablishment]
):
    for dinesafeto_establishment in old_parsed_dinesafetoestablishments.values():
        convert_dinesafeto_inspection(dinesafeto_establishment=dinesafeto_establishment)
