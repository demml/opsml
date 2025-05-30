INSERT INTO opsml_space_name
(space, name, registry_type) 
VALUES ($1, $2, $3)
ON CONFLICT(space, name, registry_type)
DO UPDATE SET updated_at = CURRENT_TIMESTAMP;