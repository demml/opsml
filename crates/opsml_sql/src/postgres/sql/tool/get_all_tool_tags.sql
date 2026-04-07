SELECT DISTINCT jsonb_array_elements_text(tags::jsonb) AS tag
FROM opsml_tool_registry
WHERE space = $1 AND tags IS NOT NULL
