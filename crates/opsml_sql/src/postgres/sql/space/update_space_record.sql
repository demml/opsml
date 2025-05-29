UPDATE opsml_space SET 
    description = $1,
    updated_at = CURRENT_TIMESTAMP
WHERE space = $2;