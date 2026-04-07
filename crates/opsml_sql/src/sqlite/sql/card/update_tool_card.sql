UPDATE opsml_tool_registry SET
app_env = ?,
name = ?,
space = ?,
tags = ?,
tool_type = ?,
args_schema = ?,
description = ?,
content_hash = ?,
username = ?,
opsml_version = ?
WHERE uid = ?;
