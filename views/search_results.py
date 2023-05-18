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

inspection_md_str = """
<p style="color:{status_color}">
    Inspection on {inspection_dt_str}: {status}
</p>
"""


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

        for inspection in inspections:
            status_color = "Green" if inspection.is_pass else "Red"
            status = "Pass" if inspection.is_pass else "Fail"
            inspection_dt_str = datetime.fromtimestamp(inspection.timestamp).strftime(
                "%Y-%m-%d"
            )
            st.markdown(
                inspection_md_str.format(
                    status_color=status_color,
                    status=status,
                    inspection_dt_str=inspection_dt_str,
                ),
                unsafe_allow_html=True,
            )
            with st.expander("details"):
                st.write(json.loads(inspection.details_json))

        st.markdown("----")
