from typing import List, Tuple

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
    add_new_establishment_if_not_exists,
    add_new_inspection_if_not_exists,
    get_establishments,
    get_inspections,
)
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


def refresh_dinesafeto_and_update_db():
    p = download_dinesafeto()
    dinesafetoestablishments = get_parsed_dinesafetoestablishments(path_to_xml=p)
    with open(LAST_REFRESHED_TS_P, mode="w") as f:
        f.write(str(time.time()))

    with DB_ENGINE.connect() as conn:
        with open("dinesafe/data/db/sql/create_establishment.sql") as f:
            conn.execute(text(f.read()))
        with open("dinesafe/data/db/sql/create_inspection.sql") as f:
            conn.execute(text(f.read()))
        for dinesafetoestablishment in dinesafetoestablishments.values():
            establishment = convert_dinesafeto_establishment(
                dinesafeto_establishment=dinesafetoestablishment
            )
            inspections = convert_dinesafeto_inspection(
                dinesafeto_establishment=dinesafetoestablishment
            )
            add_new_establishment_if_not_exists(conn=conn, establishment=establishment)
            for inspection in inspections:
                add_new_inspection_if_not_exists(conn=conn, inspection=inspection)
        conn.commit()
    return None


if should_refresh:
    with st.spinner("Refreshing data..."):
        refresh_dinesafeto_and_update_db()
        with open(LAST_REFRESHED_TS_P) as f:
            last_refreshed_ts = float(f.read())


@st.experimental_singleton()
def get_cached_establishments() -> List[Tuple[Establishment, Inspection]]:
    out = []
    with DB_ENGINE.connect() as conn:
        establishments = get_establishments(conn=conn)
        for establishment in establishments:
            inspections = get_inspections(conn=conn, establishment=establishment)
            out.append((establishment, inspections))
    return out


ESTABLISHMENTS = get_cached_establishments()
st.write(ESTABLISHMENTS)

with st.sidebar:
    st.markdown(
        "Data is taken from [open.toronto.ca](https://open.toronto.ca/dataset/dinesafe/)."
    )
    if st.button("Refresh data"):
        should_refresh = True

    if should_refresh:
        with st.spinner("Refreshing data..."):
            logger.info("Refreshing due to user request.")
            refresh_dinesafeto_and_update_db()
            st.experimental_singleton.clear()

    num_minutes = (last_refreshed_ts + REFRESH_SECONDS - time.time()) // 60
    st.markdown(
        f"{format_number(len(ESTABLISHMENTS))} establishments loaded. \n\n"
        f"Next refresh in {format_timespan(num_seconds=60*num_minutes)}. \n\n"
        "Github: [tianle91/dinesafe](https://github.com/tianle91/dinesafe)"
    )


if len(ESTABLISHMENTS) == 0:
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
