from typing import List

from rapidfuzz import fuzz, utils


def get_name_distances(search_term: str, doc_strs: List[str]) -> List[float]:
    return [
        # fuzz.WRatio returns similarity between 0 and 100
        1.0 - fuzz.WRatio(search_term, s, processor=utils.default_process) / 100.0
        for s in doc_strs
    ]
