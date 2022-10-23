from typing import List, Tuple

import pandas as pd
import pydeck
import streamlit as st

from ds_types import Establishment

establishment_icon_data_default = {
    "url": "https://upload.wikimedia.org/wikipedia/commons/6/64/Icone_Vermelho.svg",
    "width": 242,
    "height": 242,
    "anchorY": 242,
}

establishment_icon_data_by_ranking = {
    0: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Eo_circle_deep-orange_number-1.svg",
        "width": 242,
        "height": 242,
        "anchorY": 242,
    },
    1: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/85/Eo_circle_deep-orange_number-2.svg",
        "width": 242,
        "height": 242,
        "anchorY": 242,
    },
    2: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Eo_circle_deep-orange_number-3.svg",
        "width": 242,
        "height": 242,
        "anchorY": 242,
    },
    3: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Eo_circle_deep-orange_white_number-4.svg",
        "width": 242,
        "height": 242,
        "anchorY": 242,
    },
    4: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/f9/Eo_circle_deep-orange_number-5.svg",
        "width": 242,
        "height": 242,
        "anchorY": 242,
    },
}

self_icon_data = {
    "url": "https://upload.wikimedia.org/wikipedia/commons/3/35/Location_dot_blue.svg",
    "width": 242,
    "height": 242,
    "anchorY": 242,
}


def map_results(most_relevant: List[Establishment], center_loc: Tuple[float, float]):
    lat, lon = center_loc
    self_df = pd.DataFrame([{
        'lat': lat,
        'lon': lon,
        'icon_data': self_icon_data
    }])
    self_layer = pydeck.Layer(
        'IconLayer',
        data=self_df,
        get_icon="icon_data",
        size_scale=30,
        get_position=["lon", "lat"],
        pickable=False,
    )

    establishment_df = pd.DataFrame(data=[
        {
            'lon': est.longitude,
            'lat': est.latitude,
            'name': est.name,
            'status': est.status,
            'icon_data': establishment_icon_data_by_ranking.get(i, establishment_icon_data_default),
        }
        for i, est in enumerate(most_relevant)
    ])
    establishment_layer = pydeck.Layer(
        'IconLayer',
        data=establishment_df,
        get_icon="icon_data",
        size_scale=30,
        get_position=["lon", "lat"],
        pickable=True,
    )

    r = pydeck.Deck(
        layers=[self_layer, establishment_layer],
        map_style='road',
        initial_view_state=pydeck.data_utils.compute_view(points=establishment_df),
        tooltip={
            'html': '{name} ({status})',
            'style': {
                'color': 'white'
            }
        },
    )
    st.pydeck_chart(r)
