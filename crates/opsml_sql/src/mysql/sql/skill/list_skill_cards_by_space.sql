SELECT s.* FROM opsml_skill_registry s
INNER JOIN (
    SELECT name, MAX(major) AS max_major, MAX(minor) AS max_minor, MAX(patch) AS max_patch
    FROM opsml_skill_registry WHERE space = ? GROUP BY name
) latest ON s.name = latest.name
    AND s.major = latest.max_major
    AND s.minor = latest.max_minor
    AND s.patch = latest.max_patch
WHERE s.space = ? ORDER BY s.name
