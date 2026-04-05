SELECT DISTINCT j.value
FROM opsml_subagent_registry, json_each(tags) AS j
WHERE space = ? AND tags IS NOT NULL AND json_valid(tags)
