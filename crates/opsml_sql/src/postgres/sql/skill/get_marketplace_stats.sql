SELECT COUNT(*), COUNT(DISTINCT space), COALESCE(SUM(download_count), 0)
FROM opsml_skill_registry
