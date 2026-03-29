SELECT DISTINCT jsonb_array_elements_text(tags::jsonb) AS tag
FROM opsml_skill_registry
WHERE tags IS NOT NULL
