from typing import List, Tuple

import streamlit as st
from datetime import datetime
from views.yelp_ratings import get_formatted_yelp_business_rating
from dinesafe.data.db.types import Establishment, Inspection

summary_md_str = """
#### {rank}. **{name}**
*Address: {address}*

<p style="color:{status_color}">
    {status}
    (Last inspected on: {last_inspection_dt_str})
</p>
"""


def search_results(most_relevant: List[Tuple[Establishment, Inspection]]):
    for i, establishment_inspection in enumerate(most_relevant):
        establishment, latest_inspection = establishment_inspection

        last_inspection_dt_str = "NA"
        if latest_inspection is not None:
            last_inspection_dt_str = datetime.fromtimestamp(
                latest_inspection.timestamp
            ).strftime("%Y-%m-%d")

        status_color = "Green" if latest_inspection.is_pass else "Red"
        md_str = summary_md_str.format(
            rank=i + 1,
            name=establishment.name,
            address=establishment.address,
            status_color=status_color,
            status="Pass" if latest_inspection.is_pass else "Fail",
            last_inspection_dt_str=last_inspection_dt_str,
        )
        st.markdown(md_str, unsafe_allow_html=True)

        yelp_rating_md_str = get_formatted_yelp_business_rating(
            establishment=establishment
        )
        st.markdown(yelp_rating_md_str, unsafe_allow_html=True)

        st.markdown("----")
