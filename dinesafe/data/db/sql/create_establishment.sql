CREATE TABLE IF NOT EXISTS establishment (
    establishment_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    details_json TEXT,
    PRIMARY KEY (establishment_id)
)
