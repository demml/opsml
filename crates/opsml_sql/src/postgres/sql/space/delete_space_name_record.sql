DELETE FROM opsml_space_name
WHERE space = $1
AND name = $2
AND registry_type = $3;
