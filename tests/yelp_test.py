from dinesafe.data.dinesafeto.parsed import (
    get_parsed_establishments,
)
from dinesafe.yelp import get_yelp_biz_search_top_result
from dinesafe.data.db.types import Establishment
from dinesafe.data.dinesafeto.convert import convert_dinesafeto_establishment


def test_get_yelp_biz_search_result():
    dinesafeto_establishments = get_parsed_establishments(
        path_to_xml="tests/test_data/dinesafe/old.xml"
    )

    for dinesafeto_establishment in dinesafeto_establishments.values():
        establishment = convert_dinesafeto_establishment(
            dinesafeto_establishment=dinesafeto_establishment
        )
        yelp_biz_result = get_yelp_biz_search_top_result(establishment=establishment)
        assert yelp_biz_result is not None
        break
