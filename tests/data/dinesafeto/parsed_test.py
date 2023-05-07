import pytest

from dinesafe.data.dinesafeto.parsed import get_parsed_dinesafetoestablishments


@pytest.mark.parametrize(
    ("path_to_xml", "num_establishments"),
    [
        pytest.param("tests/test_data/dinesafe/new.xml", 3, id="new"),
        pytest.param("tests/test_data/dinesafe/old.xml", 2, id="old"),
    ],
)
def test_get_parsed_establishments(path_to_xml: str, num_establishments: int):
    d = get_parsed_dinesafetoestablishments(path_to_xml=path_to_xml)
    assert len(d) == num_establishments, len(d)
