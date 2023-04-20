from dinesafe.parsed import (
    get_parsed_establishments,
    Establishment,
    get_new_establishments,
    get_new_inspections,
)
from dinesafe.data import DataSource

NEW_ESTABLISHMENTS = get_parsed_establishments("tests/test_data/dinesafe/new.xml")
OLD_ESTABLISHMENTS = get_parsed_establishments("tests/test_data/dinesafe/old.xml")


def test_data_source(data_source: DataSource):
    establishments = get_parsed_establishments(data_source.latest_path)
    assert len(establishments) > 1
    for establishment in establishments.values():
        assert isinstance(establishment, Establishment)
        break


def test_get_new_establishments():
    actual = get_new_establishments(new=NEW_ESTABLISHMENTS, old=OLD_ESTABLISHMENTS)
    assert len(actual) == 1


def test_get_new_inspections():
    actual = get_new_inspections(new=NEW_ESTABLISHMENTS, old=OLD_ESTABLISHMENTS)
    assert len(actual) == 1
    for new_inspections_by_date in actual.values():
        assert len(new_inspections_by_date) == 1
        break
