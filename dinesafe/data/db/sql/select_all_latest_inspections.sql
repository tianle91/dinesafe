WITH max_timestamps AS (
    SELECT
        establishment_id,
        MAX(timestamp) AS max_timestamp
    FROM inspection
    GROUP BY establishment_id
)
SELECT
    inspection_id,
    inspection.establishment_id,
    is_pass,
    timestamp,
    details_json
    -- we just want to exclude max_timestamp
FROM inspection
INNER JOIN max_timestamps
ON inspection.establishment_id = max_timestamps.establishment_id
    AND inspection.timestamp = max_timestamps.max_timestamp
