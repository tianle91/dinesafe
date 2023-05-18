from dinesafe.data.types import Establishment, Inspection

ESTABLISHMENT_ID = "0"
ESTABLISHMENT_ID_1 = "1"

ESTABLISHMENT_NAME = "establishment_0"
ESTABLISHMENT_NAME_1 = "establishment_1"

ESTABLISHMENT = Establishment(
    establishment_id=ESTABLISHMENT_ID,
    name=ESTABLISHMENT_NAME,
    address="address_0",
    latitude=0.0,
    longitude=0.0,
    updated_timestamp=0.0,
)

ESTABLISHMENT_1 = Establishment(
    establishment_id=ESTABLISHMENT_ID_1,
    name=ESTABLISHMENT_NAME_1,
    address="address_1",
    latitude=0.0,
    longitude=0.0,
    updated_timestamp=0.0,
)

INSPECTION = Inspection(
    inspection_id="1",
    establishment_id=ESTABLISHMENT_ID,
    is_pass=True,
    timestamp=0,
    updated_timestamp=0.0,
)
