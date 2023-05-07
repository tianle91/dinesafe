import pytest

from dinesafe.data.dinesafeto.parsed import get_parsed_establishments


# old_parsed_establishments: Dict[str, DinesafeTOEstablishment]
@pytest.fixture(scope="session", autouse=True)
def old_parsed_establishments():
    return get_parsed_establishments(path_to_xml="tests/test_data/dinesafe/old.xml")
