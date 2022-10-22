from typing import List, Tuple

import pandas as pd
import pydeck
import streamlit as st

from ds_types import Establishment

establishment_icon_data = {
    "url": "https://upload.wikimedia.org/wikipedia/commons/6/64/Icone_Vermelho.svg",
    "width": 242,
    "height": 242,
    "anchorY": 242,
}

self_icon_data = {
    "url": "https://upload.wikimedia.org/wikipedia/commons/3/35/Location_dot_blue.svg",
    "width": 242,
    "height": 242,
    "anchorY": 242,
}


def map_results(most_relevant: List[Establishment], center_loc: Tuple[float, float]):
    lat, lon = center_loc
    establishment_df = pd.DataFrame(data=[
        {
            'lon': est.longitude,
            'lat': est.latitude,
            'name': est.name,
            'status': est.status,
            'icon_data': establishment_icon_data,
        }
        for est in most_relevant
    ])
    self_df = pd.DataFrame([{
        'lat': lat,
        'lon': lon,
        'icon_data': self_icon_data
    }])

    r = pydeck.Deck(
        layers=[
            pydeck.Layer(
                'IconLayer',
                data=self_df,
                get_icon="icon_data",
                size_scale=15,
                get_position=["lon", "lat"],
                pickable=False,
            ),
            pydeck.Layer(
                'IconLayer',
                data=establishment_df,
                get_icon="icon_data",
                size_scale=15,
                get_position=["lon", "lat"],
                pickable=True,
            ),
        ],
        map_style='road',
        initial_view_state=pydeck.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=17,
            min_zoom=19,
            pitch=0,
            bearing=0
        ),
        tooltip={
            'html': '{name} ({status})',
            'style': {
                'color': 'white'
            }
        },
    )
    st.pydeck_chart(r)
