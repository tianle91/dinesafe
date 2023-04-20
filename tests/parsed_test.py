from dinesafe.parsed import get_parsed_establishments
from dinesafe.data import DataSource


def test_data_source():
    ds = DataSource()
    assert ds.refresh_and_get_latest_path() is not None
    assert len(get_parsed_establishments(ds.latest_path)) > 1
