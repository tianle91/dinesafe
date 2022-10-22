from dataclasses import dataclass
from typing import List, Optional

import streamlit as st

from ds_types import YMD_FORMAT, Establishment, Inspection
from get_parsed import establishments


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


def get_similarity(search_term: str, establishment: Establishment) -> float:
    search_terms = search_term.lower().split()
    estab_name = establishment.name.lower()
    return len([s for s in search_terms if s in estab_name]) / len(search_terms)


st.title('Dinesafe')


search_term = st.text_input(
    label=f'Search for business name (out of {len(establishments)})',
    value='New Hong Fatt',
    help='Just enter some words on the business name correctly.'
)

closest_establishments: List[Establishment] = sorted(
    establishments,
    key=lambda estab: get_similarity(search_term=search_term, establishment=estab),
    reverse=True
)

for establishment in closest_establishments[:10]:
    latest_inspections: List[Inspection] = sorted(
        establishment.inspection,
        key=lambda insp: insp.date,
        reverse=True
    )
    latest_inspection = latest_inspections[0] if len(latest_inspections) > 0 else None

    summary_md_str = f'''
    **{establishment.name}**
    *Address: {establishment.address}*
    '''

    if latest_inspection is None:
        continue
    else:
        summary_md_str += f'''
        *{establishment.status}*
        *(Last inspected on: {latest_inspection.date.strftime(YMD_FORMAT)})*
        '''

    st.markdown(summary_md_str)

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
