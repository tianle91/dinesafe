from typing import Dict

from dinesafe.data.dinesafeto.convert import convert_dinesafeto_establishment
from dinesafe.data.dinesafeto.types import Establishment
from dinesafe.yelp import get_yelp_biz_search_top_result


def test_get_yelp_biz_search_result(
    old_parsed_dinesafetoestablishments: Dict[str, Establishment]
):
    for dinesafeto_establishment in old_parsed_dinesafetoestablishments.values():
        establishment = convert_dinesafeto_establishment(
            dsto_estab=dinesafeto_establishment
        )
        yelp_biz_result = get_yelp_biz_search_top_result(establishment=establishment)
        assert yelp_biz_result is not None
        break
