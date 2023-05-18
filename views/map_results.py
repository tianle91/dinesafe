from typing import List, Optional, Tuple

import pandas as pd
import pydeck
import streamlit as st

from dinesafe.data.types import Establishment, Inspection

establishment_icon_data_default = {
    "url": "https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/map_icons/default.svg",
    "width": 100,
    "height": 100,
}

establishment_icon_data_by_ranking = {
    0: {
        "url": "https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/map_icons/1.svg",
        "width": 100,
        "height": 100,
    },
    1: {
        "url": "https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/map_icons/2.svg",
        "width": 100,
        "height": 100,
    },
    2: {
        "url": "https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/map_icons/3.svg",
        "width": 100,
        "height": 100,
    },
    3: {
        "url": "https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/map_icons/4.svg",
        "width": 100,
        "height": 100,
    },
    4: {
        "url": "https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/map_icons/5.svg",
        "width": 100,
        "height": 100,
    },
}

self_icon_data = {
    "url": "https://raw.githubusercontent.com/tianle91/dinesafe/main/assets/map_icons/self.svg",
    "width": 100,
    "height": 100,
}


def map_results(
    most_relevant: List[Tuple[Establishment, List[Inspection]]],
    center_loc: Optional[Tuple[float, float]] = None,
):
    data = []
    for i, v in enumerate(most_relevant):
        establishment, inspections = v
        data.append(
            {
                "lon": establishment.longitude,
                "lat": establishment.latitude,
                "name": establishment.name,
                "status": ("Pass" if inspections[0].is_pass else "Fail")
                if len(inspections) > 0
                else "No inspections",
                "icon_data": establishment_icon_data_by_ranking.get(
                    i, establishment_icon_data_default
                ),
            }
        )
    establishment_df = pd.DataFrame(data=data)
    establishment_layer = pydeck.Layer(
        "IconLayer",
        data=establishment_df,
        get_icon="icon_data",
        size_scale=30,
        get_position=["lon", "lat"],
        pickable=True,
    )

    if center_loc is not None:
        lat, lon = center_loc
        self_df = pd.DataFrame(
            [
                {
                    "lon": lon,
                    "lat": lat,
                    "name": "Your Location",
                    "status": "",
                    "icon_data": self_icon_data,
                }
            ]
        )
        self_layer = pydeck.Layer(
            "IconLayer",
            data=self_df,
            get_icon="icon_data",
            size_scale=30,
            get_position=["lon", "lat"],
            pickable=False,
        )
        layers = [self_layer, establishment_layer]
        points = pd.concat([self_df, establishment_df], axis=0)
    else:
        layers = [establishment_layer]
        points = establishment_df

    r = pydeck.Deck(
        layers=layers,
        map_style="road",
        initial_view_state=pydeck.data_utils.compute_view(points=points),
        tooltip={"html": "{name} ({status})", "style": {"color": "white"}},
    )
    st.pydeck_chart(r)
