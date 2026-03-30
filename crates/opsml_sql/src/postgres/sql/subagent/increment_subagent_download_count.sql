UPDATE opsml_subagent_registry
SET download_count = download_count + 1
WHERE uid = $1
