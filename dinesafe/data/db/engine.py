from sqlalchemy import create_engine
from sqlalchemy import Engine


def get_mysql_engine(
    user: str, password: str, url: str, database: str, port: int = 3306, **kwargs
) -> Engine:
    return create_engine(
        f"mysql+mysqlconnector://{user}:{password}@{url}:{port}/{database}", **kwargs
    )


def get_inmemory_engine(**kwargs) -> Engine:
    return create_engine("sqlite+pysqlite:///:memory:", **kwargs)
