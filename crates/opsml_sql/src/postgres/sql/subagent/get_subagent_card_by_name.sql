SELECT * FROM opsml_subagent_registry
WHERE space = $1 AND name = $2
ORDER BY major DESC, minor DESC, patch DESC
LIMIT 1
