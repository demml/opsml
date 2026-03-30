SELECT * FROM (
    SELECT s.*, ROW_NUMBER() OVER (PARTITION BY s.name ORDER BY s.major DESC, s.minor DESC, s.patch DESC) AS rn
    FROM opsml_subagent_registry s
    WHERE s.space = ?
) ranked WHERE rn = 1
ORDER BY name
