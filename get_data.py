import os
from glob import glob

import requests
import wget

from get_parsed import DEFAULT_XML_FNAME

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


def get_downloaded_fname():

    print('Removing all xml files...')
    for p in glob('*.xml'):
        print(f'removing {p}')
        os.remove(p)

    url = resource_metadata['result']['url']
    filename = wget.download(url, out=DEFAULT_XML_FNAME)
    return filename


if __name__ == '__main__':
    filename = get_downloaded_fname()
    print(f'Downloaded dinesafe data to: {filename}')
