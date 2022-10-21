from dataclasses import dataclass
from datetime import date
from typing import List, Optional


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
    infraction: Infraction


@dataclass
class Establishment:
    id: str
    name: str
    type: str
    address: str
    latitude: float
    longitude: float
    status: str
    inspection: List[Inspection]
