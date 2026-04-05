SELECT * FROM (
    SELECT DISTINCT ON (name) *
    FROM opsml_tool_registry
    WHERE space = $1
    ORDER BY name, major DESC, minor DESC, patch DESC
) latest
ORDER BY download_count DESC
LIMIT $2
