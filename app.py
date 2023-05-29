import logging
import os

import requests
import requests_cache
import streamlit as st
from streamlit_js_eval import get_geolocation

from dinesafe.data.types import Establishment, Inspection
from dinesafe.distances.geo import parse_geolocation
from views.map_results import map_results
from views.search_results import search_results

requests_cache.install_cache(
    name="yelp_api_cache",
    backend="sqlite",
    urls_expire_after={
        "*": 0,
        # 1 day
        "api.yelp.com": 86400,
    },
)

logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}


GOOGLE_ANALYTICS_TAG = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-1XV37TNLTG"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-1XV37TNLTG');
</script>
"""
st.markdown(body=GOOGLE_ANALYTICS_TAG, unsafe_allow_html=True)


SHOW_TOP_N_RELEVANT = 25
REFRESH_SECONDS = 43200  # 12 hours

st.title("DinesafeTO")
st.markdown(
    """
Data is taken from [open.toronto.ca](https://open.toronto.ca/dataset/dinesafe/).
Github: [tianle91/dinesafe](https://github.com/tianle91/dinesafe)
"""
)


search_term = st.text_input(
    label="Search for business name (leave empty for all businesses)",
    value="New Hong Fatt",
    help="Just enter some words on the business name correctly.",
)
geolocation = None
if st.checkbox("Near me"):
    geo_d = get_geolocation()
    if geo_d is not None:
        geolocation = parse_geolocation(geo_d)


most_relevant = []
if geolocation is None and len(search_term) == 0:
    st.error('Either a search term or "Near Me" must be selected for search.')
else:
    with st.spinner("Getting results..."):
        search_response = requests.get(
            url=os.path.join(API_URL, "search"),
            headers=HEADERS,
            params={
                "search_term": search_term,
                "latitude": geolocation.coords.latitude
                if geolocation is not None
                else None,
                "longitude": geolocation.coords.longitude
                if geolocation is not None
                else None,
                "accuracy": geolocation.coords.accuracy
                if geolocation is not None
                else None,
            },
        )
        if search_response.status_code != 200:
            st.warning("Failed to get search result.")
        try:
            for estab_d, inspection_ds in search_response.json():
                try:
                    establishment = Establishment(**estab_d)
                except Exception as e:
                    logger.fatal(f"Failed to parse into Establishment: {estab_d}")
                    raise e
                inspections = []
                for inspection_d in inspection_ds:
                    try:
                        inspection = Inspection(**inspection_d)
                    except Exception as e:
                        logger.fatal(f"Failed to parse into Inspection: {inspection_d}")
                        raise e
                    inspections.append(inspection)
                most_relevant.append((establishment, inspections))
        except Exception as e:
            logger.fatal(f"Failed to parse json: {search_response.json()}")
            raise e


st.markdown("----")
if len(most_relevant) == 0:
    st.warning("No relevant establishments found.")
else:
    map_results(
        most_relevant=most_relevant,
        center_loc=(
            [geolocation.coords.latitude, geolocation.coords.longitude]
            if geolocation is not None
            else None
        ),
    )
    st.markdown("----")
    search_results(most_relevant=most_relevant)
