UPDATE opsml_tool_registry
SET download_count = download_count + 1
WHERE uid = ?
