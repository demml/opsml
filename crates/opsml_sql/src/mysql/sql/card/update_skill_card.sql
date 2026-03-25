UPDATE opsml_skill_registry SET
app_env = ?,
name = ?,
space = ?,
tags = ?,
compatible_tools = ?,
dependencies = ?,
description = ?,
license = ?,
content_hash = ?,
username = ?,
opsml_version = ?,
input_schema = ?
WHERE uid = ?;
