from dinesafe.data import DataSource


def test_data_source():
    ds = DataSource()
    assert ds.refresh_and_get_latest_path() is not None
    assert len(ds.timestamps) == 1
