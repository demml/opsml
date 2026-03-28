SELECT DISTINCT jt.tag
FROM opsml_skill_registry,
JSON_TABLE(tags, '$[*]' COLUMNS(tag VARCHAR(255) PATH '$')) AS jt
WHERE tags IS NOT NULL
