import pytest
from dinesafe.data import DataSource


@pytest.fixture(scope="session", autouse=True)
def data_source() -> DataSource:
    ds = DataSource()
    ds.refresh_and_get_latest_path()
    return ds
