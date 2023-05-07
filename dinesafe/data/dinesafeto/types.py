from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DinesafeTOInfraction:
    severity: str
    deficiency: str
    action: str
    conviction_date: Optional[date] = None
    court_outcome: Optional[str] = None
    amount_fined: Optional[float] = None


@dataclass
class DinesafeTOInspection:
    status: str
    date: date
    infractions: List[DinesafeTOInfraction]


@dataclass
class DinesafeTOEstablishment:
    id: str
    name: str
    type: str
    address: str
    latitude: float
    longitude: float
    status: str
    inspections: Dict[date, List[DinesafeTOInspection]]
