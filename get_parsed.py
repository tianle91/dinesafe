from pathlib import Path
from typing import List

import xmltodict

from ds_types import Establishment, get_establishment

DEFAULT_XML_FNAME = 'ds_od_xml.xml'


def get_parsed_establishments(p=DEFAULT_XML_FNAME) -> List[Establishment]:
    establishment_l = []
    if Path(p).is_file():
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
    else:
        print(f'File not found {p}')
    return []
