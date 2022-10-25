from dataclasses import dataclass
from math import radians
from typing import List, Optional, Tuple

import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances, haversine_distances
from streamlit_js_eval import get_geolocation

from get_data import get_downloaded_fname
from get_parsed import DEFAULT_XML_FNAME, get_parsed_establishments
from views.map_results import map_results
from views.search_results import search_results

SHOW_TOP_N_RELEVANT = 5


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


with st.sidebar:
    st.markdown('Data is taken from [open.toronto.ca](https://open.toronto.ca/dataset/dinesafe/).')
    if st.button('Refresh data'):
        with st.spinner('Refreshing data...'):
            assert get_downloaded_fname() == DEFAULT_XML_FNAME
        st.experimental_singleton.clear()
        establishments = get_parsed_establishments_cached()
    st.markdown(f'{len(establishments)} establishments loaded.')
    st.markdown('''[tianle91/dinesafe](https://github.com/tianle91/dinesafe)''')


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
    st.success(
        'Centering on '
        f"{geolocation.coords.latitude:.4f}, {geolocation.coords.longitude:.4f}"
    )
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
)[:SHOW_TOP_N_RELEVANT]
most_relevant_establishments = [est for est, _ in most_relevant_establishments]


if geolocation is not None:
    st.markdown('----')
    map_results(
        most_relevant=most_relevant_establishments,
        center_loc=[geolocation.coords.latitude, geolocation.coords.longitude],
    )
st.markdown('----')
search_results(most_relevant=most_relevant_establishments)
