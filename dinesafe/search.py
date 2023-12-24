from typing import Dict, List, Optional

import numpy as np

from dinesafe.data.types import Establishment
from dinesafe.distances import normalize
from dinesafe.distances.geo import Coords, get_haversine_distances
from dinesafe.distances.name import get_name_distances


def get_relevant_establishments(
    establishments_list: List[Establishment],
    coords: Optional[Coords] = None,
    search_term: Optional[str] = None,
) -> List[Establishment]:
    name_ds = [1.0 for _ in establishments_list]
    if search_term is not None and len(search_term) > 0:
        name_ds = get_name_distances(
            search_term=search_term, doc_strs=[e.name for e in establishments_list]
        )
        name_ds = list(normalize(arr=np.array(name_ds)))

    geo_ds = [1.0 for _ in establishments_list]
    if coords is not None:
        geo_ds = get_haversine_distances(
            center_loc=[coords.latitude, coords.longitude],
            locs=[(e.latitude, e.longitude) for e in establishments_list],
        )
        geo_ds = list(normalize(arr=np.array(geo_ds)))

    ranked = sorted(
        [
            (e, name_d, geo_d)
            for e, name_d, geo_d in zip(establishments_list, name_ds, geo_ds)
        ],
        key=lambda i: i[1] + i[2],
    )
    return [i[0] for i in ranked]
