SELECT * FROM (
    SELECT t.*, ROW_NUMBER() OVER (PARTITION BY t.name ORDER BY t.major DESC, t.minor DESC, t.patch DESC) AS rn
    FROM opsml_tool_registry t
    WHERE t.space = ? AND (? IS NULL OR t.tool_type = ?)
) ranked WHERE rn = 1
ORDER BY name
