from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances

from ds_types import YMD_FORMAT, Establishment, Inspection
from get_parsed import get_parsed_establishments


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


with st.spinner(f'Indexing {len(establishments)} establishments...'):
    establishment_names = [est.name for est in establishments]
    tfidf = TfidfVectorizer().fit(establishment_names)
    establishment_vecs = tfidf.transform(establishment_names)

search_term = st.text_input(
    label=f'Search for business name (out of {len(establishments)})',
    value='New Hong Fatt',
    help='Just enter some words on the business name correctly.'
)

closest_establishments: List[Establishment] = [
    establishments[i] for i in get_closest_indices(
        search_term=search_term,
        tfidf=tfidf,
        source_vecs=establishment_vecs
    )
]

summary_md_str = '''
**{name}**
*Address: {address}*

*{status}*
*(Last inspected on: {last_inspection_dt_str})*
'''

for establishment in closest_establishments[:10]:
    latest_inspections: List[Inspection] = sorted(
        establishment.inspection,
        key=lambda insp: insp.date,
        reverse=True
    )
    last_inspection = latest_inspections[0] if len(latest_inspections) > 0 else None

    last_inspection_dt_str = 'NA'
    if last_inspection is not None:
        last_inspection_dt_str = last_inspection.date.strftime(YMD_FORMAT)
        last_inspection_deficiencies = [
            infraction.deficiency
            for infraction in last_inspection.infraction
        ]

    md_str = summary_md_str.format(
        name=establishment.name,
        address=establishment.address,
        status=establishment.status,
        last_inspection_dt_str=last_inspection_dt_str,
    )
    for s in last_inspection_deficiencies:
        md_str += f'\n* {s}'
    st.markdown(md_str)

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
