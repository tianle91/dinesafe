import logging
from typing import Dict

import requests_cache
import streamlit as st
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from streamlit_js_eval import get_geolocation

from dinesafe.data.parsed import (
    download_dinesafeto,
    get_establishments_from_xml,
    get_latest_dinesafeto_xml,
)
from dinesafe.data.types import Establishment
from dinesafe.distances.geo import Coords, parse_geolocation
from dinesafe.search import get_relevant_establishments
from views.map_results import map_results
from views.search_results import search_results

scheduler = BackgroundScheduler()
scheduler.start()


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


with open("google_analytics_tag.html") as f:
    st.markdown(body=f.read(), unsafe_allow_html=True)


SHOW_TOP_N_RELEVANT = 25
REFRESH_HOURS = 12

st.markdown(
    """ # DinesafeTO
Data is taken from [open.toronto.ca](https://open.toronto.ca/dataset/dinesafe/).
Github: [tianle91/dinesafe](https://github.com/tianle91/dinesafe)
"""
)


@st.cache_resource(ttl=REFRESH_HOURS * 60 * 60)
def get_all_establishments() -> Dict[str, Establishment]:
    # get establishments and refresh scheduler
    dinesafe_xml_path = get_latest_dinesafeto_xml()
    if dinesafe_xml_path is None:
        download_dinesafeto()
        dinesafe_xml_path = get_latest_dinesafeto_xml()
    if dinesafe_xml_path is None:
        raise ValueError("Unable to find a dinesafeto xml file")
    scheduler.add_job(
        func=download_dinesafeto,
        trigger=IntervalTrigger(hours=12),
        # the following 3 options should make this add_job idempotent
        replace_existing=False,
        max_instances=1,
        id="download_dinesafeto",
    )
    return get_establishments_from_xml(dinesafe_xml_path)


establishments = get_all_establishments()


@st.cache_resource(ttl=REFRESH_HOURS * 60 * 60)
def get_failed_establishments():
    return [e for e in establishments.values() if not e.passed_most_recent_inspection]


failed_establishments = get_failed_establishments()

st.write(
    f"Loaded {len(establishments)} establishments "
    f"with {len(failed_establishments)} failed inspections."
)


# toronto union station
DEFAULT_LAT_LON = 43.6453, -79.3806

# get search parameters from url or input
EXISTING_QUERY_PARAMS = st.experimental_get_query_params()
search_term_default = EXISTING_QUERY_PARAMS.get("search_term", [""])[0]
latitude = float(EXISTING_QUERY_PARAMS.get("latitude", [DEFAULT_LAT_LON[0]])[0])
longitude = float(EXISTING_QUERY_PARAMS.get("longitude", [DEFAULT_LAT_LON[1]])[0])
search_term = st.text_input(
    label="Search for business name (leave empty for all businesses)",
    value=search_term_default,
    help="Just enter some words on the business name correctly.",
)

# get geolocation
geo_d = None
if st.checkbox("Near me"):
    geo_d = get_geolocation()
    if geo_d is not None:
        geolocation = parse_geolocation(geo_d)
        latitude = geolocation.coords.latitude
        longitude = geolocation.coords.longitude
if geo_d is None:
    st.warning("No location provided, using defaults.")

st.experimental_set_query_params(
    search_term=search_term,
    latitude=latitude,
    longitude=longitude,
)

st.info(f"Will search for establishments near: `{latitude}, {longitude}`")

most_relevant = []
with st.spinner("Getting results..."):
    coords = None
    if latitude is not None and longitude is not None:
        coords = Coords(latitude=latitude, longitude=longitude)
    most_relevant = get_relevant_establishments(
        establishments_list=list(establishments.values()),
        coords=coords,
        search_term=search_term,
    )
if len(most_relevant) == 0:
    st.warning("No relevant establishments found. Please retry later.")
else:
    most_relevant = most_relevant[:SHOW_TOP_N_RELEVANT]
    st.markdown(f"Showing top {SHOW_TOP_N_RELEVANT} relevant establishments.")

map_results(
    most_relevant=most_relevant,
    center_loc=(latitude, longitude),
)
search_results(most_relevant=most_relevant)
