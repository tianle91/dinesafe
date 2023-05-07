from dinesafe.data.db.types import Establishment, Inspection
from typing import Dict
from datetime import date


def add_new_establishment_if_not_exists(establishment: Establishment):
    pass


def add_new_inspection_if_not_exists(inspection: Inspection):
    pass


def get_establishments() -> Dict[str, Establishment]:
    pass


def get_inspections(establishment: Establishment):
    pass


def get_new_inspections_since(dt: date):
    pass
