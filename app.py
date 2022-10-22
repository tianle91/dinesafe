from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances

from ds_types import Establishment
from get_parsed import get_parsed_establishments
from views.search_results import search_results
from typing import Tuple


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
    distances = [(i, d) for i, d in enumerate(
        cosine_distances(source_vecs, search_term_vecs).reshape(-1))]
    closest = sorted(distances, key=lambda x: x[1])[:10]
    return [x[0] for x in closest]


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

most_relevant_establishments: List[Establishment] = [
    establishments[i] for i in get_closest_indices(
        search_term=search_term,
        tfidf=tfidf,
        source_vecs=establishment_vecs
    )
]

search_results(most_relevant=most_relevant_establishments)

# from streamlit_js_eval import get_geolocation
# if st.checkbox("Center on my location"):
#     geolocation = parse_geolocation(get_geolocation())
#     st.write(
#         f"Your coordinates are {geolocation.coords.latitude:.4f}, {geolocation.coords.longitude:.4f}")
#     st.map(
#         data=pd.DataFrame({
#             'lat': [geolocation.coords.latitude],
#             'lon': [geolocation.coords.longitude],
#         }),
#         zoom=17,
#     )
