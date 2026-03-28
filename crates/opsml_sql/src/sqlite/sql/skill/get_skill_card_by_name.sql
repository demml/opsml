SELECT * FROM opsml_skill_registry
WHERE space = ? AND name = ?
ORDER BY major DESC, minor DESC, patch DESC
LIMIT 1
