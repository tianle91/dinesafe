import glob
import logging
import os
import time
from typing import List, Optional

import wget

logger = logging.getLogger(__name__)
LAST_REFRESHED_TS_FNAME = "LAST_REFRESHED_TS"

# alternative sources
# https://open.toronto.ca/dataset/dinesafe/
# https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/dinesafe
URL = "https://secure.toronto.ca/opendata/ds/od_xml/v2?format=xml&stream=n"


class DataSource:
    def __init__(self, base_path: str = "data/dinesafe") -> None:
        os.makedirs(base_path, exist_ok=True)
        self.base_path = base_path

    @property
    def paths(self) -> List[str]:
        return list(glob.glob(os.path.join(self.base_path, "*.xml")))

    @property
    def timestamps(self) -> List[float]:
        return sorted(
            [float(os.path.splitext(os.path.basename(p))[0]) for p in self.paths],
            reverse=True,
        )

    @property
    def latest_timestamp(self) -> Optional[float]:
        return self.timestamps[0] if len(self.timestamps) > 0 else None

    @property
    def time_since_latest_timestamp(self) -> Optional[float]:
        now_ts = time.time()
        return (
            now_ts - self.latest_timestamp
            if self.latest_timestamp is not None
            else None
        )

    @property
    def latest_path(self) -> Optional[str]:
        return (
            os.path.join(self.base_path, f"{self.latest_timestamp}.xml")
            if self.latest_timestamp is not None
            else None
        )

    def refresh_and_get_latest_path(self) -> Optional[str]:
        now_ts = time.time()
        download_fname = f"{now_ts}.xml"
        download_path = os.path.join(self.base_path, download_fname)
        logger.info(f"Downloading to {download_path}")
        try:
            wget.download(URL, out=download_path)
            return download_path
        except Exception as e:
            logger.error(str(e))
        return None
