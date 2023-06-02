from typing import List, Optional

import numpy as np
from sqlalchemy import Connection

from dinesafe.data.io import get_all_establishments
from dinesafe.distances import normalize
from dinesafe.distances.geo import Coords, get_haversine_distances
from dinesafe.distances.name import get_name_distances


def get_relevant_establishment_ids(
    conn: Connection,
    coords: Optional[Coords] = None,
    search_term: Optional[str] = None,
) -> List[str]:
    all_estabs = get_all_establishments(conn=conn)

    name_ds = [1.0 for _ in all_estabs]
    if search_term is not None and len(search_term) > 0:
        name_ds = get_name_distances(
            search_term=search_term, doc_strs=[e.name for e in all_estabs]
        )
        name_ds = list(normalize(arr=np.array(name_ds)))

    geo_ds = [1.0 for _ in all_estabs]
    if coords is not None:
        geo_ds = get_haversine_distances(
            center_loc=[coords.latitude, coords.longitude],
            locs=[(e.latitude, e.longitude) for e in all_estabs],
        )
        geo_ds = list(normalize(arr=np.array(geo_ds)))

    ranked = sorted(
        [
            (e.establishment_id, name_d, geo_d)
            for e, name_d, geo_d in zip(all_estabs, name_ds, geo_ds)
        ],
        key=lambda i: i[1] + i[2],
    )
    return [i[0] for i in ranked]
