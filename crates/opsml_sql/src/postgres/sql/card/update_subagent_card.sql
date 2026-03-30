UPDATE opsml_subagent_registry SET
app_env = $1,
name = $2,
space = $3,
tags = $4,
compatible_clis = $5,
description = $6,
content_hash = $7,
username = $8,
opsml_version = $9
WHERE uid = $10;
