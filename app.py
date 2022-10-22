from dataclasses import dataclass
from typing import List, Optional
from streamlit_js_eval import get_geolocation

import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances

from ds_types import Establishment
from get_parsed import get_parsed_establishments
from views.search_results import search_results
from typing import Tuple
import pandas as pd

from math import radians
from typing import List, Tuple
from sklearn.metrics.pairwise import haversine_distances

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


def parse_geolocation(d) -> GeoLocation:
    return GeoLocation(
        coords=Coords(**d.get('coords', {})),
        timestamp=d.get('timestamp'),
    )


def get_closest_indices(
    search_term: str,
    tfidf: TfidfVectorizer,
    source_vecs: np.ndarray,
) -> List[int]:
    search_term_vecs = tfidf.transform([search_term])
    distances = [
        (i, d)
        for i, d in enumerate(cosine_distances(
            source_vecs,
            search_term_vecs
        ).reshape(-1))
    ]
    closest_first = sorted(distances, key=lambda x: x[1])
    return [x[0] for x in closest_first]


st.markdown('''
# DinesafeTO
Data is taken from [open.toronto.ca](https://open.toronto.ca/dataset/dinesafe/).
''')

if st.button('Refresh data'):
    with open('get_data.py') as f:
        exec(f.read())


establishments = get_parsed_establishments()

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
    label=f'Search for business name (out of {len(establishments)})',
    value='New Hong Fatt',
    help='Just enter some words on the business name correctly.'
)


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


# if st.checkbox("Near me"):
#     geolocation = parse_geolocation(get_geolocation())
#     # st.write(
#     #     f"Your coordinates are {geolocation.coords.latitude:.4f}, {geolocation.coords.longitude:.4f}")

#     establishment_locs = [
#         [establishment.latitude, establishment.longitude]
#         for establishment in establishments
#     ]
#     establishment_distances = get_haversine_distances(
#         center_loc=[geolocation.coords.latitude, geolocation.coords.longitude],
#         locs=establishment_locs,
#     )

#     st.map(
#         data=pd.DataFrame({
#             'lat': [geolocation.coords.latitude],
#             'lon': [geolocation.coords.longitude],
#         }),
#         zoom=17,
#     )


most_relevant_establishments: List[Establishment] = establishments[:SHOW_TOP_N_RELEVANT]
if len(search_term) > 0:
    most_relevant_establishments: List[Establishment] = [
        establishments[i] for i in get_closest_indices(
            search_term=search_term,
            tfidf=tfidf,
            source_vecs=establishment_vecs
        )[:SHOW_TOP_N_RELEVANT]
    ]

search_results(most_relevant=most_relevant_establishments)
