import time
from dataclasses import dataclass
from math import radians
from typing import List, Optional, Tuple

import numpy as np
import streamlit as st
from humanfriendly import format_number, format_timespan
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances, haversine_distances
from streamlit_js_eval import get_geolocation

from get_data import (LAST_DOWNLOADED_TIMESTAMP_FILE, REFRESH_SECONDS,
                      refresh_xml_file, refresh_xml_file_if_stale)
from get_parsed import get_parsed_establishments
from views.map_results import map_results
from views.search_results import search_results

SHOW_TOP_N_RELEVANT = 10


@dataclass
class Coords:
    accuracy: float
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    altitudeAccuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None


@dataclass
class GeoLocation:
    coords: Coords
    timestamp: int


def parse_geolocation(d: dict) -> GeoLocation:
    return GeoLocation(
        coords=Coords(**d.get('coords', {})),
        timestamp=d.get('timestamp'),
    )


def get_name_distances(
    search_term: str,
    tfidf: TfidfVectorizer,
    source_vecs: np.ndarray,
) -> List[float]:
    search_term_vecs = tfidf.transform([search_term])
    return list(cosine_distances(source_vecs, search_term_vecs).reshape(-1))


st.title('DinesafeTO')


@st.experimental_singleton
def get_parsed_establishments_cached():
    return get_parsed_establishments()


establishments = get_parsed_establishments_cached()

refresh_xml_file_if_stale()
with st.sidebar:
    st.markdown('Data is taken from [open.toronto.ca](https://open.toronto.ca/dataset/dinesafe/).')
    if st.button('Refresh data'):
        with st.spinner('Refreshing data...'):
            refresh_xml_file()
            st.experimental_singleton.clear()
    with open(LAST_DOWNLOADED_TIMESTAMP_FILE) as f:
        last_downloaded_ts = float(f.read())
        seconds_till_refresh = last_downloaded_ts + REFRESH_SECONDS - time.time()
        # round to minutes
        minutes_till_refresh = int(seconds_till_refresh / 60)
    st.markdown(
        f'{format_number(len(establishments))} establishments loaded. \n\n'
        f'Next refresh in {format_timespan(num_seconds=60*minutes_till_refresh)}. \n\n'
        'Github: [tianle91/dinesafe](https://github.com/tianle91/dinesafe)'
    )


if len(establishments) == 0:
    st.warning('No establishments loaded. Please refresh data')
    st.stop()


@st.experimental_singleton
def get_tfidfs(establishment_names: List[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
    tfidf = TfidfVectorizer().fit(establishment_names)
    establishment_vecs = tfidf.transform(establishment_names)
    return tfidf, establishment_vecs


with st.spinner(f'Indexing {len(establishments)} establishments...'):
    establishment_names = [est.name for est in establishments]
    tfidf, establishment_vecs = get_tfidfs(establishment_names=establishment_names)

search_term = st.text_input(
    label='Search for business name (leave empty for all businesses)',
    value='New Hong Fatt',
    help='Just enter some words on the business name correctly.'
)


name_distances = [1. for _ in establishments]
establishment_distances = [1. for _ in establishments]

if len(search_term) > 0:
    name_distances = get_name_distances(
        search_term=search_term,
        tfidf=tfidf,
        source_vecs=establishment_vecs
    )
    # normalize to range: 1, 2
    name_distances_min = min(name_distances)
    name_distances_max = max(name_distances)
    name_distances_mid = .5 * (name_distances_min + name_distances_max)
    name_distances_range = name_distances_max - name_distances_min
    name_distances = (name_distances - name_distances_mid) / (name_distances_range / 2) + 2


def get_haversine_distances(
    center_loc: Tuple[float, float],
    locs: List[Tuple[float, float]]
) -> List[float]:
    center_loc = [[radians(v) for v in center_loc]]
    locs = [
        [radians(v) for v in loc]
        for loc in locs
    ]
    return list(haversine_distances(X=locs, Y=center_loc)[:, 0])


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
    # normalize to range: 0, 1
    establishment_distances = establishment_distances / max(establishment_distances)


# find most relevant establishments
most_relevant_establishments = []
for est, d_name, d_estab in zip(establishments, name_distances, establishment_distances):
    if d_name < 1.2:
        most_relevant_establishments.append((est, d_estab))
most_relevant_establishments = sorted(
    most_relevant_establishments,
    key=lambda x: x[1]
)
num_close_names = len(most_relevant_establishments)
will_be_truncated = num_close_names > SHOW_TOP_N_RELEVANT
most_relevant_establishments = [
    est for est, _ in most_relevant_establishments[:SHOW_TOP_N_RELEVANT]
]
if will_be_truncated:
    warning_message = f'Showing top {SHOW_TOP_N_RELEVANT} out of {num_close_names}. '
    if geolocation is None:
        warning_message += 'For more relevant results, consider clicking "Near Me".'
    st.warning(warning_message)

st.markdown('----')
map_results(
    most_relevant=most_relevant_establishments,
    center_loc=(
        [geolocation.coords.latitude, geolocation.coords.longitude]
        if geolocation is not None else None
    ),
)
st.markdown('----')
search_results(most_relevant=most_relevant_establishments)
