SELECT COUNT(*), COUNT(DISTINCT name), COALESCE(SUM(download_count), 0)
FROM opsml_subagent_registry
WHERE space = $1
