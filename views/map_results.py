from typing import List, Optional, Tuple

import pandas as pd
import pydeck
import streamlit as st

from dinesafe.data.types import Establishment, Inspection

PASS_ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/f/fa/Xcode_test_case_success_green.svg"
FAIL_ICON_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/5/5e/Antu_task-reject.svg"
)
UNKNOWN_ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/b/bf/Blue_question_mark_%28italic%29.svg"


def map_results(
    most_relevant: List[Tuple[Establishment, List[Inspection]]],
    center_loc: Optional[Tuple[float, float]] = None,
):
    data = []
    for establishment, inspections in most_relevant:
        is_pass = inspections[0].is_pass if len(inspections) > 0 else None
        data.append(
            {
                "lon": establishment.longitude,
                "lat": establishment.latitude,
                "name": establishment.name,
                "status": ("?" if is_pass is None else "Pass" if is_pass else "Fail")
                if len(inspections) > 0
                else "No inspections",
                "icon_data": {
                    "url": UNKNOWN_ICON_URL
                    if is_pass is None
                    else PASS_ICON_URL
                    if is_pass
                    else FAIL_ICON_URL,
                    "width": 100,
                    "height": 100,
                },
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
                    "icon_data": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Map_pin_icon.svg",
                        "width": 94,
                        "height": 128,
                    },
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
        tooltip={"html": "{name}"},
    )
    st.pydeck_chart(r)
