from typing import List

import xmltodict

from data_source.types import Establishment, get_establishment


def get_parsed_establishments(p: str) -> List[Establishment]:
    establishment_l = []
    with open(p) as f:
        establishment_l = xmltodict.parse(f.read())['DINESAFE_DATA']['ESTABLISHMENT']
    establishments = []
    for d in establishment_l:
        try:
            establishments.append(get_establishment(d))
        except Exception as e:
            print(e)
            print(d)
            break
    return establishments
