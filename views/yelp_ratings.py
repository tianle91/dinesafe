import os
from typing import Optional

import requests
import requests_cache

from ds_types import Establishment

requests_cache.install_cache(
    backend='sqlite',
    # 1 day
    urls_expire_after={'*': 86400}
)

YELP_API_KEY = os.getenv('YELP_API_KEY', None)


rating_to_stars_url_mapping = {
    0.: 'https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_stars/regular_0.png',
    1.: 'https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_stars/regular_1.png',
    1.5: 'https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_stars/regular_1_half.png',
    2.: 'https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_stars/regular_2.png',
    2.5: 'https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_stars/regular_2_half.png',
    3.: 'https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_stars/regular_3.png',
    3.5: 'https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_stars/regular_3_half.png',
    4.: 'https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_stars/regular_4.png',
    4.5: 'https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_stars/regular_4_half.png',
    5.: 'https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_stars/regular_5.png',
}

yelp_business_md_template = '''
![{num_stars}]({stars_url})
<a href="{yelp_biz_page_url}"><img src="https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/yelp_logo.png" alt="drawing" height="20"/></a>

Based on {num_reviews} reviews.
'''


def get_yelp_biz_search_result(establishment: Establishment) -> Optional[dict]:
    if YELP_API_KEY is not None:
        response = requests.get(
            url="https://api.yelp.com/v3/businesses/search",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {YELP_API_KEY}"
            },
            params={
                'latitude': establishment.latitude,
                'longitude': establishment.longitude,
                'term': establishment.name,
            }
        )
        if response.status_code == 200:
            businesses = response.json()['businesses']
            if len(businesses) > 0:
                return businesses[0]
    return None


def get_formatted_yelp_business_rating(establishment: Establishment) -> str:
    d = get_yelp_biz_search_result(establishment=establishment)
    if d is not None:
        return yelp_business_md_template.format(
            num_stars=d['rating'],
            stars_url=rating_to_stars_url_mapping[d['rating']],
            num_reviews=d['review_count'],
            yelp_biz_page_url=d['url'],
        )
    return ''
