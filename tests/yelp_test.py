from dinesafe.data.parsed import get_establishments_from_xml
from dinesafe.yelp import get_yelp_biz_search_top_result


def test_get_yelp_biz_search_result():
    for e in get_establishments_from_xml(
        "tests/test_data/dinesafe/1000.01.xml"
    ).values():
        yelp_biz_result = get_yelp_biz_search_top_result(establishment=e)
        assert yelp_biz_result is not None
        break
