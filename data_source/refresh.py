import os
import time
from typing import Optional

import wget

LAST_REFRESHED_TS_FNAME = 'LAST_REFRESHED_TS'

# alternative sources
# https://open.toronto.ca/dataset/dinesafe/
# https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/dinesafe
URL = 'https://secure.toronto.ca/opendata/ds/od_xml/v2?format=xml&stream=n'


class DataSourceRefresh:
    def __init__(self, base_path: str = 'data/dinesafe', refresh_seconds: int = 43200) -> None:
        '''
        Refreshes by default every 43200 seconds (12 hours).
        '''
        os.makedirs(base_path, exist_ok=True)
        self.base_path = base_path
        self.refresh_seconds = refresh_seconds

    @property
    def last_refreshed_ts_path(self) -> str:
        return os.path.join(self.base_path, LAST_REFRESHED_TS_FNAME)

    def get_last_refreshed_ts(self) -> Optional[float]:
        if not os.path.isfile(self.last_refreshed_ts_path):
            return None
        else:
            with open(self.last_refreshed_ts_path) as f:
                return float(f.read())

    def get_latest_path(self) -> Optional[str]:
        last_refreshed_ts = self.get_last_refreshed_ts()
        if last_refreshed_ts is None:
            return None
        else:
            return os.path.join(self.base_path, f'{last_refreshed_ts}.xml')

    def get_seconds_since_last_refresh(self) -> Optional[int]:
        last_refreshed_ts = self.get_last_refreshed_ts()
        if last_refreshed_ts is None:
            return None
        else:
            time_since_last_refresh = time.time() - last_refreshed_ts
            return time_since_last_refresh

    def is_stale(self) -> bool:
        seconds_since_last_refresh = self.get_seconds_since_last_refresh()
        if seconds_since_last_refresh is None:
            return True
        else:
            return seconds_since_last_refresh > self.refresh_seconds

    def get_refreshed_if_stale(self) -> str:
        if self.is_stale():
            now_ts = time.time()
            download_fname = f'{now_ts}.xml'
            download_path = os.path.join(self.base_path, download_fname)
            print(f'Found stale, downloading to {download_path}')
            wget.download(URL, out=download_path)
            with open(self.last_refreshed_ts_path, 'w') as f:
                f.write(str(now_ts))
            return download_path
        else:
            latest_path = self.get_latest_path()
            print(f'Not stale yet, return latest {latest_path}')
            return latest_path


if __name__ == '__main__':
    DataSourceRefresh().get_refreshed_if_stale()
