CREATE TABLE IF NOT EXISTS inspection (
    inspection_id VARCHAR(255) NOT NULL,
    establishment_id VARCHAR(255) NOT NULL,
    is_pass BIT(1) NOT NULL,
    timestamp NUMERIC NOT NULL,
    details_json VARCHAR(65535),
    PRIMARY KEY (establishment_id, inspection_id)
    FOREIGN KEY (establishment_id) REFERENCES establishment(establishment_id)
)
