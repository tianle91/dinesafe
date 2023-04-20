from dinesafe.parsed import get_parsed_establishments, Establishment
from dinesafe.data import DataSource


def test_data_source(data_source: DataSource):
    establishments = get_parsed_establishments(data_source.latest_path)
    assert len(establishments) > 1
    assert isinstance(establishments[0], Establishment)
