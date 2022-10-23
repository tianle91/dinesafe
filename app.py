from dataclasses import dataclass
from math import radians
from typing import List, Optional, Tuple

import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances, haversine_distances
from streamlit_js_eval import get_geolocation

from get_parsed import get_parsed_establishments
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


establishments = get_parsed_establishments()


with st.sidebar:
    st.markdown('Data is taken from [open.toronto.ca](https://open.toronto.ca/dataset/dinesafe/).')
    if st.button('Refresh data'):
        with open('get_data.py') as f:
            exec(f.read())
    st.markdown(f'{len(establishments)} establishments loaded.')


if len(establishments) == 0:
    st.warning('No establishments loaded. Please refresh data')
    st.stop()


@st.cache(ttl=86400)  # 1 day ttl
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
    name_distances = name_distances / max(name_distances)


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
    establishment_distances = establishment_distances / max(establishment_distances)


composite_distances = [a + b for a, b in zip(name_distances, establishment_distances)]
most_relevant_establishments = [
    est for _, est in sorted(
        zip(composite_distances, establishments),
        key=lambda pair: pair[0]
    )
]
most_relevant_establishments = most_relevant_establishments[:SHOW_TOP_N_RELEVANT]

if geolocation is not None:
    st.markdown('----')
    map_results(
        most_relevant=most_relevant_establishments,
        center_loc=[geolocation.coords.latitude, geolocation.coords.longitude],
    )
st.markdown('----')
search_results(most_relevant=most_relevant_establishments)
