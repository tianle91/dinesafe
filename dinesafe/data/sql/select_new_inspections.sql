SELECT * FROM inspection
WHERE establishment_id = {establishment_id}
AND updated_timestamp > '{last_updated_timestamp}'
