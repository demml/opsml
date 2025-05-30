INSERT INTO opsml_space_name
(space, name, registry_type) 
VALUES (?, ?, ?)
ON DUPLICATE KEY UPDATE
    updated_at = CURRENT_TIMESTAMP;