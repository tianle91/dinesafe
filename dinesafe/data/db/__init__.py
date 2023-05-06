from sqlalchemy import create_engine
from sqlalchemy import Engine
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


def get_mysql_engine(
    user: str, password: str, url: str, database: str, port: int = 3306, **kwargs
) -> Engine:
    return create_engine(
        f"mysql+mysqlconnector://{user}:{password}@{url}:{port}/{database}", **kwargs
    )


def get_inmemory_engine(**kwargs) -> Engine:
    return create_engine("sqlite+pysqlite:///:memory:", **kwargs)


def add_new_establishments_if_not_exists():
    pass


def add_new_inspections_if_not_exists():
    pass


def get_establishments():
    pass


def get_inspections():
    pass


def get_new_inspections_since():
    pass
