SELECT * FROM (
    SELECT DISTINCT ON (name) *
    FROM opsml_skill_registry
    ORDER BY name, major DESC, minor DESC, patch DESC
) latest
ORDER BY download_count DESC
LIMIT $1
