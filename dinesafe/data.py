import glob
import logging
import os
import time
from typing import List, Optional

import wget

logger = logging.getLogger(__name__)
LAST_REFRESHED_TS_FNAME = 'LAST_REFRESHED_TS'

# alternative sources
# https://open.toronto.ca/dataset/dinesafe/
# https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/dinesafe
URL = 'https://secure.toronto.ca/opendata/ds/od_xml/v2?format=xml&stream=n'


class DataSource:
    def __init__(self, base_path: str = 'data/dinesafe', refresh_seconds: int = 43200) -> None:
        '''
        Refreshes by default every 43200 seconds (12 hours).
        '''
        os.makedirs(base_path, exist_ok=True)
        self.base_path = base_path
        self.refresh_seconds = refresh_seconds

    @property
    def paths(self) -> List[str]:
        return list(glob.glob(os.path.join(self.base_path, '*.xml')))

    @property
    def timestamps(self) -> List[float]:
        return [float(os.path.splitext(os.path.basename(p))[0]) for p in self.paths]

    def refresh_and_get_latest_path(self) -> Optional[str]:
        now_ts = time.time()
        download_fname = f'{now_ts}.xml'
        download_path = os.path.join(self.base_path, download_fname)
        logger.info(f'Downloading to {download_path}')
        try:
            wget.download(URL, out=download_path)
            return download_path
        except Exception as e:
            logger.error(str(e))
        return None
