from dataclasses import dataclass
from typing import Optional


@dataclass
class Inspection:
    inspection_id: str
    establishment_id: str
    is_pass: bool
    timestamp: float
    updated_timestamp: float
    details_json: Optional[str] = None

    def __hash__(self) -> int:
        return hash(self.inspection_id)


@dataclass
class Establishment:
    establishment_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    updated_timestamp: float
    details_json: Optional[str] = None
