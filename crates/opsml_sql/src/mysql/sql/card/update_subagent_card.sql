UPDATE opsml_subagent_registry SET
app_env = ?,
name = ?,
space = ?,
tags = ?,
compatible_clis = ?,
description = ?,
content_hash = ?,
username = ?,
opsml_version = ?
WHERE uid = ?;
