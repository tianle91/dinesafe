from dinesafe.parsed import (
    get_parsed_establishments,
    Establishment,
    get_new_establishments,
    get_new_inspections,
)
from dinesafe.data import DataSource


def test_data_source(data_source: DataSource):
    establishments = get_parsed_establishments(data_source.latest_path)
    assert len(establishments) > 1
    for establishment in establishments.values():
        assert isinstance(establishment, Establishment)
        break


def test_get_new_establishments():
    new = get_parsed_establishments("tests/data/dinesafe/new.xml")
    old = get_parsed_establishments("tests/data/dinesafe/old.xml")
    actual = get_new_establishments(new=new, old=old)
    assert len(actual) == 1


def test_get_new_inspections():
    new = get_parsed_establishments("tests/data/dinesafe/new.xml")
    old = get_parsed_establishments("tests/data/dinesafe/old.xml")
    actual = get_new_inspections(new=new, old=old)
    assert len(actual) == 1
    for new_inspections_by_date in actual.values():
        assert len(new_inspections_by_date) == 1
        break
