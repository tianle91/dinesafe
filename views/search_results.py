import json
from datetime import datetime
from typing import List, Tuple

import streamlit as st

from dinesafe.data.types import Establishment, Inspection
from views.yelp_ratings import get_formatted_yelp_business_rating

establishment_md_str = """
#### {rank}. **{name}**
*Address: {address} ({lat:.4f}, {lon:.4f})*
"""

latest_inspection_md_str = """
<p style="color:{status_color}">
    Latest inspection on {inspection_dt_str}: {status}
</p>
"""


def get_dt_str_from_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def search_results(most_relevant: List[Tuple[Establishment, List[Inspection]]]):
    for i, v in enumerate(most_relevant):
        establishment, inspections = v

        st.markdown(
            establishment_md_str.format(
                rank=i + 1,
                name=establishment.name,
                address=establishment.address,
                lat=establishment.latitude,
                lon=establishment.longitude,
            )
        )
        yelp_rating_md_str = get_formatted_yelp_business_rating(
            establishment=establishment
        )
        st.markdown(yelp_rating_md_str, unsafe_allow_html=True)

        # print the latest inspection result
        if len(inspections) > 0:
            latest_inspection = inspections[0]
            st.markdown(
                latest_inspection_md_str.format(
                    status_color="Green" if latest_inspection.is_pass else "Red",
                    status="Pass" if latest_inspection.is_pass else "Fail",
                    inspection_dt_str=get_dt_str_from_timestamp(
                        ts=latest_inspection.timestamp
                    ),
                ),
                unsafe_allow_html=True,
            )
        # older inspections if any including latest
        for inspection in inspections:
            expander_title = (
                f"Inspection on {get_dt_str_from_timestamp(inspection.timestamp)}: "
            )
            expander_title += "✅" if inspection.is_pass else "❌"
            with st.expander(expander_title):
                st.write(json.loads(inspection.details_json))
        st.markdown("----")
