SELECT DISTINCT jt.tag
FROM opsml_subagent_registry,
JSON_TABLE(tags, '$[*]' COLUMNS(tag VARCHAR(255) PATH '$')) AS jt
WHERE space = ? AND tags IS NOT NULL
