SELECT DISTINCT j.value
FROM opsml_skill_registry, json_each(tags) AS j
WHERE tags IS NOT NULL AND json_valid(tags)
