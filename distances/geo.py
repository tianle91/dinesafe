from dataclasses import dataclass
from math import radians
from typing import List, Optional, Tuple

from sklearn.metrics.pairwise import haversine_distances


@dataclass
class Coords:
    accuracy: float
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    altitudeAccuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None


@dataclass
class GeoLocation:
    coords: Coords
    timestamp: int


def parse_geolocation(d: dict) -> GeoLocation:
    return GeoLocation(
        coords=Coords(**d.get('coords', {})),
        timestamp=d.get('timestamp'),
    )


def get_haversine_distances(
    center_loc: Tuple[float, float],
    locs: List[Tuple[float, float]]
) -> List[float]:
    center_loc = [[radians(v) for v in center_loc]]
    locs = [
        [radians(v) for v in loc]
        for loc in locs
    ]
    return list(haversine_distances(X=locs, Y=center_loc)[:, 0])
