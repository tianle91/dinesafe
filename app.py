import logging
import os
import time
from typing import List, Tuple

import numpy as np
import streamlit as st
from humanfriendly import format_number, format_timespan
from sklearn.feature_extraction.text import TfidfVectorizer
from streamlit_js_eval import get_geolocation

from dinesafe.data.db.engine import get_local_engine
from dinesafe.data.db.io import (
    create_establishment_table_if_not_exists,
    create_inspection_table_if_not_exists,
    get_latest,
)
from dinesafe.data.db.types import Establishment, Inspection
from dinesafe.data.dinesafeto.refresh import refresh_dinesafeto_and_update_db
from dinesafe.distances import normalize
from dinesafe.distances.geo import get_haversine_distances, parse_geolocation
from dinesafe.distances.name import get_name_distances
from views.map_results import map_results
from views.search_results import search_results

logger = logging.getLogger(__name__)


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
LAST_REFRESHED_TS_P = "LAST_REFRESHED_TS"

DB_ENGINE = get_local_engine()

with DB_ENGINE.connect() as conn:
    create_establishment_table_if_not_exists(conn=conn)
    create_inspection_table_if_not_exists(conn=conn)

st.title("DinesafeTO")


should_refresh = False
if os.path.isfile(LAST_REFRESHED_TS_P):
    with open(LAST_REFRESHED_TS_P) as f:
        LAST_REFRESHED_TS = float(f.read())
    ts_now = time.time()
    if ts_now > LAST_REFRESHED_TS + REFRESH_SECONDS:
        should_refresh = True
        logger.info(
            f"Will refresh due to stale: {ts_now} > {LAST_REFRESHED_TS} + {REFRESH_SECONDS}"
        )
else:
    should_refresh = True
    logger.info(f"Will refresh because {LAST_REFRESHED_TS_P} is not found.")


@st.experimental_singleton()
def get_cached_all_latest_inspections() -> List[Tuple[Establishment, Inspection]]:
    with DB_ENGINE.connect() as conn:
        return get_latest(conn=conn)


with st.sidebar:
    st.markdown(
        "Data is taken from [open.toronto.ca](https://open.toronto.ca/dataset/dinesafe/)."
    )
    user_requested_refresh = st.button("Refresh data")
    if user_requested_refresh:
        logger.info("Refreshing due to user request.")
    if user_requested_refresh or should_refresh:
        with st.spinner("Refreshing data..."):
            with DB_ENGINE.connect() as conn:
                (
                    new_establishment_counts,
                    new_inspection_counts,
                ) = refresh_dinesafeto_and_update_db(conn=conn)

            st.info(
                f"Added {format_number(new_establishment_counts)} new establishments "
                + f"and {format_number(new_inspection_counts)} new inspections."
            )
            LAST_REFRESHED_TS = time.time()
            with open(LAST_REFRESHED_TS_P, mode="w") as f:
                f.write(str(LAST_REFRESHED_TS))
            st.experimental_singleton.clear()

    ALL_LATEST_INSPECTIONS = get_cached_all_latest_inspections()
    num_minutes = (LAST_REFRESHED_TS + REFRESH_SECONDS - time.time()) // 60
    st.markdown(
        f"{format_number(len(ALL_LATEST_INSPECTIONS))} establishments loaded. \n\n"
        f"Next refresh in {format_timespan(num_seconds=60*num_minutes)}. \n\n"
        "Github: [tianle91/dinesafe](https://github.com/tianle91/dinesafe)"
    )


if len(ALL_LATEST_INSPECTIONS) == 0:
    st.warning("No establishments loaded. Please refresh data")
    st.stop()


@st.experimental_singleton
def get_tfidfs(establishment_names: List[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
    tfidf = TfidfVectorizer().fit(establishment_names)
    establishment_vecs = tfidf.transform(establishment_names)
    return tfidf, establishment_vecs


with st.spinner(f"Indexing {len(ALL_LATEST_INSPECTIONS)} establishments..."):
    TFIDF, ESTABLISHMENT_TFIDF_VECS = get_tfidfs(
        establishment_names=[e.name for e, _ in ALL_LATEST_INSPECTIONS]
    )

search_term = st.text_input(
    label="Search for business name (leave empty for all businesses)",
    value="New Hong Fatt",
    help="Just enter some words on the business name correctly.",
)


NAME_DISTANCES = [1.0 for _ in ALL_LATEST_INSPECTIONS]
GEO_DISTANCES = [1.0 for _ in ALL_LATEST_INSPECTIONS]

if len(search_term) > 0:
    NAME_DISTANCES = get_name_distances(
        search_term=search_term, tfidf=TFIDF, source_vecs=ESTABLISHMENT_TFIDF_VECS
    )
    NAME_DISTANCES = normalize(arr=NAME_DISTANCES, lowest_val=1.0, hightest_val=2.0)


geolocation = None
if st.checkbox("Near me"):
    geo_d = get_geolocation()
    if geo_d is not None:
        geolocation = parse_geolocation(geo_d)

if geolocation is not None:
    establishment_locs = [
        [establishment.latitude, establishment.longitude]
        for establishment, _ in ALL_LATEST_INSPECTIONS
    ]
    GEO_DISTANCES = get_haversine_distances(
        center_loc=[geolocation.coords.latitude, geolocation.coords.longitude],
        locs=establishment_locs,
    )
    GEO_DISTANCES = normalize(arr=GEO_DISTANCES)


RELEVANT_INSPECTIONS = []
# first filter by name distance
for establishment_inspection, name_distance, geo_distance in zip(
    ALL_LATEST_INSPECTIONS, NAME_DISTANCES, GEO_DISTANCES
):
    if name_distance < 1.2:
        RELEVANT_INSPECTIONS.append((establishment_inspection, geo_distance))
# then sort by geo distance
RELEVANT_INSPECTIONS = sorted(RELEVANT_INSPECTIONS, key=lambda x: x[1])
RELEVANT_INSPECTIONS = list(map(lambda t: t[0], RELEVANT_INSPECTIONS))

# get the top relevant
num_close_names = len(RELEVANT_INSPECTIONS)
will_be_truncated = num_close_names > SHOW_TOP_N_RELEVANT
RELEVANT_INSPECTIONS = RELEVANT_INSPECTIONS[:SHOW_TOP_N_RELEVANT]
if will_be_truncated:
    warning_message = f"Showing top {SHOW_TOP_N_RELEVANT} out of {num_close_names}. "
    if geolocation is None:
        warning_message += 'For more relevant results, consider clicking "Near Me".'
    st.warning(warning_message)

st.markdown("----")
map_results(
    most_relevant=RELEVANT_INSPECTIONS,
    center_loc=(
        [geolocation.coords.latitude, geolocation.coords.longitude]
        if geolocation is not None
        else None
    ),
)
st.markdown("----")
search_results(most_relevant=RELEVANT_INSPECTIONS)
