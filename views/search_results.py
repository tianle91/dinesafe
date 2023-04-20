from typing import List

import streamlit as st

from dinesafe.constants import YMD_FORMAT
from dinesafe.parsed import Establishment, Inspection
from views.yelp_ratings import get_formatted_yelp_business_rating

summary_md_str = """
#### {rank}. **{name}**
*Address: {address}*

<p style="color:{status_color}">
    {status}
    (Last inspected on: {last_inspection_dt_str})
</p>
"""


def search_results(most_relevant: List[Establishment]):
    for i, establishment in enumerate(most_relevant):
        latest_inspections: List[Inspection] = sorted(
            establishment.inspection, key=lambda insp: insp.date, reverse=True
        )
        last_inspection = latest_inspections[0] if len(latest_inspections) > 0 else None

        last_inspection_dt_str = "NA"
        last_inspection_deficiencies = []
        if last_inspection is not None:
            last_inspection_dt_str = last_inspection.date.strftime(YMD_FORMAT)
            last_inspection_deficiencies = [
                infraction.deficiency for infraction in last_inspection.infraction
            ]

        status_color = "Green" if establishment.status.lower() == "pass" else "Red"
        md_str = summary_md_str.format(
            rank=i + 1,
            name=establishment.name,
            address=establishment.address,
            status_color=status_color,
            status=establishment.status,
            last_inspection_dt_str=last_inspection_dt_str,
        )
        st.markdown(md_str, unsafe_allow_html=True)

        if len(last_inspection_deficiencies) > 0:
            with st.expander(f"Found {len(last_inspection_deficiencies)} deficiencies"):
                md_str = ""
                for deficiency_str in last_inspection_deficiencies:
                    md_str += f"* {deficiency_str}\n"
                st.markdown(md_str)

        yelp_rating_md_str = get_formatted_yelp_business_rating(
            establishment=establishment
        )
        st.markdown(yelp_rating_md_str, unsafe_allow_html=True)

        st.markdown("----")
