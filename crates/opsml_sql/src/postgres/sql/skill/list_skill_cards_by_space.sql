SELECT DISTINCT ON (name) *
FROM opsml_skill_registry
WHERE space = $1
ORDER BY name, major DESC, minor DESC, patch DESC
