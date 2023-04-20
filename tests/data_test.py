from dinesafe.data import DataSource


def test_data_source(data_source: DataSource):
    assert len(data_source.paths) == 1
    assert len(data_source.timestamps) == 1
    assert data_source.latest_path is not None
