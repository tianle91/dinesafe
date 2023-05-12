import pytest

from dinesafe.data.dinesafeto.parsed import get_parsed_dinesafetoestablishments


@pytest.mark.parametrize(
    ("path_to_xml", "updated_timestamp", "num_establishments"),
    [
        pytest.param("tests/test_data/dinesafe/1001.11.xml", 1001.11, 3, id="new"),
        pytest.param("tests/test_data/dinesafe/1000.01.xml", 1000.01, 2, id="old"),
    ],
)
def test_get_parsed_establishments(
    path_to_xml: str, updated_timestamp: float, num_establishments: int
):
    d = get_parsed_dinesafetoestablishments(
        path_to_xml=path_to_xml, updated_timestamp=updated_timestamp
    )
    assert len(d) == num_establishments, len(d)
