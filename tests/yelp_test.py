from dinesafe.parsed import get_parsed_establishments
from dinesafe.data import DataSource
from dinesafe.yelp import get_yelp_biz_search_result


def test_get_yelp_biz_search_result(data_source: DataSource):
    establishment = get_parsed_establishments(data_source.latest_path)[0]
    get_yelp_biz_search_result(establishment=establishment)
    assert establishment.yelp_biz_result is not None
