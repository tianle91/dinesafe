from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Inspection:
    inspection_id: str
    establishment_id: str
    is_pass: bool
    date: date
    details_json: Optional[str] = None


@dataclass
class Establishment:
    establishment_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    details_json: Optional[str] = None
