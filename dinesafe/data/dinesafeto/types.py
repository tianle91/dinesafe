import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


INFRACTION_STR = """
severity: {severity}
deficiency: {deficiency}
action: {action}
conviction_date: {conviction_date}
court_outcome: {court_outcome}
amount_fined: {amount_fined}
"""


@dataclass
class Infraction:
    severity: str
    deficiency: str
    action: str
    conviction_date: Optional[datetime] = None
    court_outcome: Optional[str] = None
    amount_fined: Optional[float] = None

    def __str__(self) -> str:
        return INFRACTION_STR.format(
            severity=self.severity,
            deficiency=self.deficiency,
            action=self.action,
            conviction_date=self.conviction_date,
            court_outcome=self.court_outcome,
            amount_fined=self.amount_fined,
        )


INSPECTION_STR = """
status: {status}
date: {date}
infractions:
{infractions}
"""


@dataclass
class Inspection:
    status: str
    date: datetime
    infractions: List[Infraction]

    def __str__(self) -> str:
        return INSPECTION_STR.format(
            status=self.status,
            date=self.date,
            infractions="----\n".join(
                [str(infraction) for infraction in self.infractions]
            ),
        )


@dataclass
class Establishment:
    id: str
    name: str
    type: str
    address: str
    latitude: float
    longitude: float
    status: str
    updated_timestamp: float
    inspections: Dict[datetime, List[Inspection]]

    @property
    def external_id(self) -> str:
        return f"DinesafeTO_{self.id}"
