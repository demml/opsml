SELECT * FROM (
    SELECT DISTINCT ON (name) *
    FROM opsml_tool_registry
    WHERE space = $1 AND ($2::TEXT IS NULL OR tool_type = $2)
    ORDER BY name, major DESC, minor DESC, patch DESC
) latest
ORDER BY name
