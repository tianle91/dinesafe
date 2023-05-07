WITH max_timestamps AS (
    SELECT
        establishment_id,
        MAX(timestamp) AS max_timestamp
    FROM inspection
    GROUP BY establishment_id
)
SELECT * FROM inspection
INNER JOIN max_timestamps
ON inspection.establishment_id = max_timestamps.establishment_id
    AND inspection.timestamp = max_timestamps.max_timestamp
