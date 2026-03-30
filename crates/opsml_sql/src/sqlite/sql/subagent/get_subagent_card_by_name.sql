SELECT * FROM opsml_subagent_registry
WHERE space = ? AND name = ?
ORDER BY major DESC, minor DESC, patch DESC
LIMIT 1
