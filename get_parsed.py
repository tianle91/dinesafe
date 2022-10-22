import xmltodict

from ds_types import get_establishment

with open('ds_od_xml.xml') as f:
    ds_d = xmltodict.parse(f.read())


establishments = []
for i, d in enumerate(ds_d['DINESAFE_DATA']['ESTABLISHMENT']):
    try:
        establishments.append(get_establishment(d))
    except Exception as e:
        print(e)
        print(d)
        break
