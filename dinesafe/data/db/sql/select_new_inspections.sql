SELECT * FROM inspection
WHERE establishment_id = {establishment_id}
AND timestamp > '{last_inspection_timestamp}'
