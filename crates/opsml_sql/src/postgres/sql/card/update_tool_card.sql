UPDATE opsml_tool_registry SET
app_env = $1,
name = $2,
space = $3,
tags = $4,
tool_type = $5,
args_schema = $6,
description = $7,
content_hash = $8,
username = $9,
opsml_version = $10
WHERE uid = $11;
