SELECT * FROM opsml_subagent_registry
WHERE space = $1 AND name = $2 AND version = $3
LIMIT 1
