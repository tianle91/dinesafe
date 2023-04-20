import os
from typing import Optional

import requests
import requests_cache

from dinesafe.types import Establishment
import logging

logger = logging.getLogger(__name__)

requests_cache.install_cache(
    backend="sqlite",
    # 1 day
    urls_expire_after={"*": 86400},
)

YELP_API_KEY = os.getenv("YELP_API_KEY", None)


def get_yelp_biz_search_result(establishment: Establishment) -> Optional[dict]:
    if YELP_API_KEY is None:
        logger.error("YELP_API_KEY is None")
    else:
        response = requests.get(
            url="https://api.yelp.com/v3/businesses/search",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {YELP_API_KEY}",
            },
            params={
                "latitude": establishment.latitude,
                "longitude": establishment.longitude,
                "term": establishment.name,
            },
        )
        if response.status_code != 200:
            logger.error(f"Received non-200 response: {response}")
        else:
            businesses = response.json()["businesses"]
            if len(businesses) > 0:
                top_business_result = businesses[0]
                establishment.yelp_biz_result = top_business_result
                return top_business_result
            else:
                logger.error(
                    f"Received no business results for establishment: {establishment}"
                )
    return None
