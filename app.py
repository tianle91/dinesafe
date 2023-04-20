from typing import List, Tuple

import numpy as np
import streamlit as st
from humanfriendly import format_number, format_timespan
from sklearn.feature_extraction.text import TfidfVectorizer
from streamlit_js_eval import get_geolocation

from dinesafe.parsed import get_parsed_establishments
from dinesafe.data import DataSource

from dinesafe.distances import normalize
from dinesafe.distances.geo import get_haversine_distances, parse_geolocation
from dinesafe.distances.name import get_name_distances
from views.map_results import map_results
from views.search_results import search_results


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

ds = DataSource()
time_since_latest = ds.time_since_latest_timestamp
if time_since_latest is None or time_since_latest > REFRESH_SECONDS:
    ds.refresh_and_get_latest_path()
ds_path = ds.latest_path
if ds_path is None:
    raise ValueError("ds_path is None")


@st.experimental_singleton()
def get_parsed_establishments_cached():
    return get_parsed_establishments(p=ds_path)


establishments = get_parsed_establishments_cached()

with st.sidebar:
    st.markdown(
        "Data is taken from [open.toronto.ca](https://open.toronto.ca/dataset/dinesafe/)."
    )
    if st.button("Refresh data"):
        with st.spinner("Refreshing data..."):
            ds_path = ds.refresh_and_get_latest_path()
            st.experimental_singleton.clear()

    num_minutes = (REFRESH_SECONDS - ds.time_since_latest_timestamp) // 60
    st.markdown(
        f"{format_number(len(establishments))} establishments loaded. \n\n"
        f"Next refresh in {format_timespan(num_seconds=60*num_minutes)}. \n\n"
        "Github: [tianle91/dinesafe](https://github.com/tianle91/dinesafe)"
    )


if len(establishments) == 0:
    st.warning("No establishments loaded. Please refresh data")
    st.stop()


@st.experimental_singleton
def get_tfidfs(establishment_names: List[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
    tfidf = TfidfVectorizer().fit(establishment_names)
    establishment_vecs = tfidf.transform(establishment_names)
    return tfidf, establishment_vecs


with st.spinner(f"Indexing {len(establishments)} establishments..."):
    establishment_names = [est.name for est in establishments]
    tfidf, establishment_vecs = get_tfidfs(establishment_names=establishment_names)

search_term = st.text_input(
    label="Search for business name (leave empty for all businesses)",
    value="New Hong Fatt",
    help="Just enter some words on the business name correctly.",
)


name_distances = [1.0 for _ in establishments]
establishment_distances = [1.0 for _ in establishments]

if len(search_term) > 0:
    name_distances = get_name_distances(
        search_term=search_term, tfidf=tfidf, source_vecs=establishment_vecs
    )
    name_distances = normalize(arr=name_distances, lowest_val=1.0, hightest_val=2.0)


geolocation = None
if st.checkbox("Near me"):
    geo_d = get_geolocation()
    if geo_d is not None:
        geolocation = parse_geolocation(geo_d)

if geolocation is not None:
    establishment_locs = [
        [establishment.latitude, establishment.longitude]
        for establishment in establishments
    ]
    establishment_distances = get_haversine_distances(
        center_loc=[geolocation.coords.latitude, geolocation.coords.longitude],
        locs=establishment_locs,
    )
    establishment_distances = normalize(arr=establishment_distances)


# find most relevant establishments
most_relevant_establishments = []
for est, d_name, d_estab in zip(
    establishments, name_distances, establishment_distances
):
    if d_name < 1.2:
        most_relevant_establishments.append((est, d_estab))
most_relevant_establishments = sorted(most_relevant_establishments, key=lambda x: x[1])
num_close_names = len(most_relevant_establishments)
will_be_truncated = num_close_names > SHOW_TOP_N_RELEVANT
most_relevant_establishments = [
    est for est, _ in most_relevant_establishments[:SHOW_TOP_N_RELEVANT]
]
if will_be_truncated:
    warning_message = f"Showing top {SHOW_TOP_N_RELEVANT} out of {num_close_names}. "
    if geolocation is None:
        warning_message += 'For more relevant results, consider clicking "Near Me".'
    st.warning(warning_message)

st.markdown("----")
map_results(
    most_relevant=most_relevant_establishments,
    center_loc=(
        [geolocation.coords.latitude, geolocation.coords.longitude]
        if geolocation is not None
        else None
    ),
)
st.markdown("----")
search_results(most_relevant=most_relevant_establishments)
