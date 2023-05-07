import pytest

from dinesafe.data.dinesafeto.parsed import get_parsed_dinesafetoestablishments


# old_parsed_dinesafetoestablishments: Dict[str, DinesafeTOEstablishment]
@pytest.fixture(scope="session", autouse=True)
def old_parsed_dinesafetoestablishments():
    return get_parsed_dinesafetoestablishments(
        path_to_xml="tests/test_data/dinesafe/old.xml"
    )
