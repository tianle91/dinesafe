CREATE TABLE IF NOT EXISTS establishment (
    establishment_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(65535) NOT NULL,
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    details_json VARCHAR(65535),
    PRIMARY KEY (establishment_id)
)
