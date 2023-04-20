from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances


def get_name_distances(
    search_term: str,
    tfidf: TfidfVectorizer,
    source_vecs: np.ndarray,
) -> List[float]:
    search_term_vecs = tfidf.transform([search_term])
    return list(cosine_distances(source_vecs, search_term_vecs).reshape(-1))
