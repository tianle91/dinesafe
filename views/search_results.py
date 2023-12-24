from datetime import datetime
from typing import List

import streamlit as st

from dinesafe.data.types import Establishment, Inspection
from views.yelp_ratings import get_formatted_yelp_business_rating


def get_dt_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


infraction_md_str = """
#### {date_str}
- Severity: {severity}
- Deficiency: {deficiency}
"""


def show_latest_inspection_results(inspection: Inspection):
    with st.expander(
        label=f'Details of inspection on {get_dt_str(inspection.date)} {"✅" if inspection.is_pass else "❌"}'
    ):
        for infraction in inspection.infractions:
            st.markdown(
                infraction_md_str.format(
                    date_str=get_dt_str(infraction.conviction_date)
                    if infraction.conviction_date is not None
                    else "???",
                    severity=infraction.severity,
                    deficiency=infraction.deficiency,
                )
            )


establishment_md_str = """
### {rank}. **{name}**
*Address: {address} ({lat:.4f}, {lon:.4f})*
"""


def search_results(most_relevant: List[Establishment]):
    for i, establishment in enumerate(most_relevant):
        st.markdown(
            establishment_md_str.format(
                rank=i + 1,
                name=establishment.name,
                address=establishment.address,
                lat=establishment.latitude,
                lon=establishment.longitude,
            )
        )
        inspections = establishment.inspections_latest_first
        if len(inspections) > 0:
            show_latest_inspection_results(inspection=inspections[0])
            pass_proportion = sum(
                [1 if inspection.is_pass else 0 for inspection in inspections]
            ) / len(inspections)
            st.markdown(
                f"Past {len(inspections)} inspections "
                + f"({100*pass_proportion:.0f}% pass rate). "
                + "Most recent first: "
                + "".join(
                    ["✅" if inspection.is_pass else "❌" for inspection in inspections]
                )
            )
        st.markdown(
            get_formatted_yelp_business_rating(establishment=establishment),
            unsafe_allow_html=True,
        )
        st.markdown("----")
