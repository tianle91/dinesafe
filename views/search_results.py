from typing import List

import streamlit as st

from ds_types import YMD_FORMAT, Establishment, Inspection

summary_md_str = '''
**{name}**
*Address: {address}*

*{status}*
*(Last inspected on: {last_inspection_dt_str})*
'''


def search_results(most_relevant: List[Establishment]):
    for establishment in most_relevant[:10]:
        latest_inspections: List[Inspection] = sorted(
            establishment.inspection,
            key=lambda insp: insp.date,
            reverse=True
        )
        last_inspection = latest_inspections[0] if len(latest_inspections) > 0 else None

        last_inspection_dt_str = 'NA'
        last_inspection_deficiencies = []
        if last_inspection is not None:
            last_inspection_dt_str = last_inspection.date.strftime(YMD_FORMAT)
            last_inspection_deficiencies = [
                infraction.deficiency
                for infraction in last_inspection.infraction
            ]

        md_str = summary_md_str.format(
            name=establishment.name,
            address=establishment.address,
            status=establishment.status,
            last_inspection_dt_str=last_inspection_dt_str,
        )
        for s in last_inspection_deficiencies:
            md_str += f'\n* {s}'
        st.markdown(md_str)
