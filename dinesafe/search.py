from functools import lru_cache
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import Connection

from dinesafe.data.io import get_all_establishments
from dinesafe.distances import normalize
from dinesafe.distances.geo import Coords, get_haversine_distances
from dinesafe.distances.name import get_name_distances


@lru_cache(maxsize=2)
def _get_tfidfs(establishment_names: Tuple[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
    tfidf = TfidfVectorizer().fit(establishment_names)
    establishment_vecs = tfidf.transform(establishment_names)
    return tfidf, establishment_vecs


def get_relevant_establishment_ids(
    conn: Connection,
    coords: Optional[Coords] = None,
    search_term: Optional[str] = None,
) -> List[str]:
    all_estabs = get_all_establishments(conn=conn)
    establishment_names = tuple(e.name for e in all_estabs)
    if len(establishment_names) == 0:
        return []

    tfidf, estab_vecs = _get_tfidfs(establishment_names=establishment_names)
    estab_locs = [(e.latitude, e.longitude) for e in all_estabs]

    name_ds = [1.0 for _ in all_estabs]
    if search_term is not None and len(search_term) > 0:
        name_ds = get_name_distances(
            search_term=search_term, tfidf=tfidf, source_vecs=estab_vecs
        )
        name_ds = list(
            normalize(arr=np.array(name_ds), lowest_val=1.0, hightest_val=2.0)
        )

    geo_ds = [1.0 for _ in all_estabs]
    if coords is not None:
        geo_ds = get_haversine_distances(
            center_loc=[coords.latitude, coords.longitude],
            locs=estab_locs,
        )
        geo_ds = list(normalize(arr=np.array(geo_ds)))

    df = pd.DataFrame(
        data=[
            {
                "name_distance": name_d,
                "geo_distance": geo_d,
                "establishment_id": e.establishment_id,
            }
            for name_d, geo_d, e in zip(name_ds, geo_ds, all_estabs)
        ]
    )
    df = df[df["name_distance"] < 1.2]
    df = df.sort_values(by="geo_distance", ascending=True)
    return list(df["establishment_id"])
