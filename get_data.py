import os
import time
from glob import glob

import requests
import wget

from get_parsed import DEFAULT_XML_FNAME

LAST_DOWNLOADED_TIMESTAMP_FILE = 'LAST_DOWNLOADED_TIMESTAMP_FILE.txt'
REFRESH_SECONDS = 43200  # 12 hours


def get_url() -> str:
    # get resource_metadata

    # Toronto Open Data is stored in a CKAN instance. It's APIs are documented here:
    # https://docs.ckan.org/en/latest/api/

    # To hit our API, you'll be making requests to:
    base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

    # Datasets are called "packages". Each package can contain many "resources"
    # To retrieve the metadata for this package and its resources, use the package name in this page's URL:
    url = base_url + "/api/3/action/package_show"
    params = {"id": "dinesafe"}
    package = requests.get(url, params=params).json()

    # To get resource data:
    for idx, resource in enumerate(package["result"]["resources"]):

        # To get metadata for non datastore_active resources:
        if not resource["datastore_active"]:
            url = base_url + "/api/3/action/resource_show?id=" + resource["id"]
            resource_metadata = requests.get(url).json()
            print(resource_metadata)
            # From here, you can use the "url" attribute to download this file

    return resource_metadata['result']['url']


def refresh_xml_file():
    print('Removing all xml files...')
    for p in glob('*.xml'):
        print(f'removing {p}')
        os.remove(p)

    url = get_url()
    wget.download(url, out=DEFAULT_XML_FNAME)

    with open(LAST_DOWNLOADED_TIMESTAMP_FILE, 'w') as f:
        now_ts = time.time()
        f.write(str(now_ts))


def refresh_xml_file_if_stale():
    is_stale = False
    if not os.path.isfile(LAST_DOWNLOADED_TIMESTAMP_FILE):
        is_stale = True
    else:
        with open(LAST_DOWNLOADED_TIMESTAMP_FILE) as f:
            last_downloaded_ts = float(f.read())
        if (time.time() - last_downloaded_ts) > REFRESH_SECONDS:
            is_stale = True
    if is_stale:
        refresh_xml_file()


if __name__ == '__main__':
    refresh_xml_file()
