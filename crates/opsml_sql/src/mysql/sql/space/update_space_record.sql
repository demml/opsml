UPDATE opsml_space SET 
    description = ?,
    updated_at = CURRENT_TIMESTAMP
WHERE space = ?;