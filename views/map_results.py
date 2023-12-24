from typing import List, Optional, Tuple

import folium
import streamlit as st
from folium.map import Icon
from streamlit_folium import folium_static

from dinesafe.data.types import Establishment


def map_results(
    most_relevant: List[Establishment],
    center_loc: Optional[Tuple[float, float]] = None,
    n_limit_bounds: Optional[int] = 1,
):
    m = folium.Map(location=center_loc, control_scale=True)
    if center_loc is not None:
        folium.Marker(
            location=center_loc,
            tooltip="Current location",
            icon=Icon(color="blue"),
        ).add_to(m)

    estab_lat_lons = []
    for i, establishment in enumerate(most_relevant):
        is_pass = establishment.passed_most_recent_inspection
        icon = str(i + 1) if i < 9 else "circle"
        color = "orange" if is_pass is None else ("green" if is_pass else "red")
        status = "unknown" if is_pass is None else ("pass" if is_pass else "fail")

        folium.Marker(
            location=[establishment.latitude, establishment.longitude],
            tooltip=f"{establishment.name} ({status})",
            icon=Icon(icon=icon, color=color, prefix="fa"),
        ).add_to(m)
        estab_lat_lons.append((establishment.latitude, establishment.longitude))

    # fit center and first n_limit_bounds establishments
    m.fit_bounds(
        bounds=[
            center_loc,
        ]
        + estab_lat_lons[:n_limit_bounds]
    )

    # https://github.com/randyzwitch/streamlit-folium/issues/7
    make_map_responsive = """
        <style>
        [title~="st.iframe"] { width: 100%}
        </style>
        """
    st.markdown(make_map_responsive, unsafe_allow_html=True)
    folium_static(m, width=500, height=500)
