from typing import List, Tuple, Dict

import numpy as np
import streamlit as st
from humanfriendly import format_number, format_timespan
from sklearn.feature_extraction.text import TfidfVectorizer
from streamlit_js_eval import get_geolocation
from dinesafe.data.dinesafeto.convert import (
    convert_dinesafeto_establishment,
    convert_dinesafeto_inspection,
)
from dinesafe.distances import normalize
from dinesafe.distances.geo import get_haversine_distances, parse_geolocation
from dinesafe.distances.name import get_name_distances
from views.map_results import map_results
from views.search_results import search_results
import os
from dinesafe.data.dinesafeto.parsed import (
    download_dinesafeto,
    get_parsed_dinesafetoestablishments,
)
import time
from dinesafe.data.db.engine import get_local_engine
from dinesafe.data.db.io import (
    create_establishment_table_if_not_exists,
    create_inspection_table_if_not_exists,
    add_new_establishment,
    add_new_inspections,
    get_all_establishments,
    get_all_latest_inspections,
)
from dinesafe.data.dinesafeto.refresh import refresh_dinesafeto_and_update_db
from dinesafe.data.db.types import Establishment, Inspection
from sqlalchemy import text
import logging

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
        last_refreshed_ts = float(f.read())
    ts_now = time.time()
    if ts_now > last_refreshed_ts + REFRESH_SECONDS:
        should_refresh = True
        logger.info(
            f"Will refresh due to stale: {ts_now} > {last_refreshed_ts} + {REFRESH_SECONDS}"
        )
else:
    should_refresh = True
    logger.info(f"Will refresh because {LAST_REFRESHED_TS_P} is not found.")


@st.experimental_singleton()
def get_cached_all_latest_inspections() -> Dict[str, Tuple[Establishment, Inspection]]:
    with DB_ENGINE.connect() as conn:
        all_establishments = {
            establishment.establishment_id: establishment
            for establishment in get_all_establishments(conn=conn)
        }
        all_latest_inspections = {
            inspection.establishment_id: inspection
            for inspection in get_all_latest_inspections(conn=conn)
        }
        # some debugging
        estab_ids = set(all_establishments.keys())
        inspection_estab_ids = set(all_latest_inspections.keys())
        if len(inspection_estab_ids - estab_ids) != 0:
            logger.warning(
                f"There are inspections without establishments: {inspection_estab_ids - estab_ids}"
            )
        return {
            k: (all_establishments[k], all_latest_inspections[k])
            for k in all_latest_inspections
        }


ALL_LATEST_INSPECTIONS = get_cached_all_latest_inspections()
for v in ALL_LATEST_INSPECTIONS.values():
    st.write(v)
    break

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
            last_refreshed_ts = time.time()
            with open(LAST_REFRESHED_TS_P, mode="w") as f:
                f.write(str(last_refreshed_ts))
            st.experimental_singleton.clear()
            st.warning("Please refresh page.")
            st.stop()

    num_minutes = (last_refreshed_ts + REFRESH_SECONDS - time.time()) // 60
    st.markdown(
        f"{format_number(len(ALL_LATEST_INSPECTIONS))} establishments loaded. \n\n"
        f"Next refresh in {format_timespan(num_seconds=60*num_minutes)}. \n\n"
        "Github: [tianle91/dinesafe](https://github.com/tianle91/dinesafe)"
    )


if len(ALL_LATEST_INSPECTIONS) == 0:
    st.warning("No establishments loaded. Please refresh data")
    st.stop()


# @st.experimental_singleton
# def get_tfidfs(establishment_names: List[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
#     tfidf = TfidfVectorizer().fit(establishment_names)
#     establishment_vecs = tfidf.transform(establishment_names)
#     return tfidf, establishment_vecs


# with st.spinner(f"Indexing {len(ESTABLISHMENTS)} establishments..."):
#     establishment_names = [est.name for est in ESTABLISHMENTS.values()]
#     tfidf, establishment_vecs = get_tfidfs(establishment_names=establishment_names)

# search_term = st.text_input(
#     label="Search for business name (leave empty for all businesses)",
#     value="New Hong Fatt",
#     help="Just enter some words on the business name correctly.",
# )


# name_distances = [1.0 for _ in ESTABLISHMENTS]
# establishment_distances = [1.0 for _ in ESTABLISHMENTS]

# if len(search_term) > 0:
#     name_distances = get_name_distances(
#         search_term=search_term, tfidf=tfidf, source_vecs=establishment_vecs
#     )
#     name_distances = normalize(arr=name_distances, lowest_val=1.0, hightest_val=2.0)


# geolocation = None
# if st.checkbox("Near me"):
#     geo_d = get_geolocation()
#     if geo_d is not None:
#         geolocation = parse_geolocation(geo_d)

# if geolocation is not None:
#     establishment_locs = [
#         [establishment.latitude, establishment.longitude]
#         for establishment in ESTABLISHMENTS.values()
#     ]
#     establishment_distances = get_haversine_distances(
#         center_loc=[geolocation.coords.latitude, geolocation.coords.longitude],
#         locs=establishment_locs,
#     )
#     establishment_distances = normalize(arr=establishment_distances)


# # find most relevant establishments
# most_relevant_establishments = []
# for est, d_name, d_estab in zip(
#     ESTABLISHMENTS.values(), name_distances, establishment_distances
# ):
#     if d_name < 1.2:
#         most_relevant_establishments.append((est, d_estab))
# most_relevant_establishments = sorted(most_relevant_establishments, key=lambda x: x[1])
# num_close_names = len(most_relevant_establishments)
# will_be_truncated = num_close_names > SHOW_TOP_N_RELEVANT
# most_relevant_establishments = [
#     est for est, _ in most_relevant_establishments[:SHOW_TOP_N_RELEVANT]
# ]
# if will_be_truncated:
#     warning_message = f"Showing top {SHOW_TOP_N_RELEVANT} out of {num_close_names}. "
#     if geolocation is None:
#         warning_message += 'For more relevant results, consider clicking "Near Me".'
#     st.warning(warning_message)

# st.markdown("----")
# map_results(
#     most_relevant=most_relevant_establishments,
#     center_loc=(
#         [geolocation.coords.latitude, geolocation.coords.longitude]
#         if geolocation is not None
#         else None
#     ),
# )
# st.markdown("----")
# search_results(most_relevant=most_relevant_establishments)
