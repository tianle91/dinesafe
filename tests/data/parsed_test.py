import pytest

from dinesafe.data.parsed import get_establishments_from_xml


@pytest.mark.parametrize(
    ("path_to_xml", "expected_num_establishments"),
    [
        pytest.param("tests/test_data/dinesafe/1001.11.xml", 3, id="new"),
        pytest.param("tests/test_data/dinesafe/1000.01.xml", 2, id="old"),
    ],
)
def test_get_establishments_from_xml(
    path_to_xml: str, expected_num_establishments: int
):
    d = get_establishments_from_xml(path_to_xml=path_to_xml)
    assert len(d) == expected_num_establishments, len(d)
