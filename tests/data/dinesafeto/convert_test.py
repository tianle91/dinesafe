from dinesafe.data.dinesafeto.parsed import (
    get_parsed_establishments,
)
from dinesafe.data.dinesafeto.convert import (
    convert_dinesafeto_establishment,
    convert_dinesafeto_inspection,
)


def test_convert_dinesafeto_establishment():
    dinesafeto_establishments = get_parsed_establishments(
        path_to_xml="tests/test_data/dinesafe/old.xml"
    )
    for dinesafeto_establishment in dinesafeto_establishments.values():
        convert_dinesafeto_establishment(
            dinesafeto_establishment=dinesafeto_establishment
        )


def test_convert_dinesafeto_inspection():
    dinesafeto_establishments = get_parsed_establishments(
        path_to_xml="tests/test_data/dinesafe/old.xml"
    )
    for dinesafeto_establishment in dinesafeto_establishments.values():
        convert_dinesafeto_inspection(dinesafeto_establishment=dinesafeto_establishment)
