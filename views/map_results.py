from typing import List, Optional, Tuple

import folium
import streamlit as st
from folium.map import Icon
from streamlit_folium import folium_static

from dinesafe.data.types import Establishment, Inspection


def map_results(
    most_relevant: List[Tuple[Establishment, List[Inspection]]],
    center_loc: Optional[Tuple[float, float]] = None,
):
    all_lat_lons = []
    m = folium.Map(location=center_loc, control_scale=True)
    if center_loc is not None:
        folium.Marker(
            location=center_loc,
            tooltip="Current location",
            icon=Icon(color="blue"),
        ).add_to(m)
        all_lat_lons.append(center_loc)

    for establishment, inspections in most_relevant:
        is_pass = inspections[0].is_pass if len(inspections) > 0 else None
        icon, color = "question", "orange"
        if is_pass is not None and is_pass:
            icon, color = "tick", "green"
        else:
            icon, color = "xmark", "red"

        folium.Marker(
            location=[establishment.latitude, establishment.longitude],
            tooltip=establishment.name,
            icon=Icon(icon=icon, color=color, prefix="fa"),
        ).add_to(m)
        all_lat_lons.append((establishment.latitude, establishment.longitude))

    m.fit_bounds(bounds=all_lat_lons)

    make_map_responsive = """
        <style>
        [title~="st.iframe"] { width: 100%}
        </style>
        """
    st.markdown(make_map_responsive, unsafe_allow_html=True)
    folium_static(m, width=500, height=500)
