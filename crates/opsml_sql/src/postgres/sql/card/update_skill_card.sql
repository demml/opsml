UPDATE opsml_skill_registry SET
app_env = $1,
name = $2,
space = $3,
tags = $4,
compatible_tools = $5,
dependencies = $6,
description = $7,
license = $8,
content_hash = $9,
username = $10,
opsml_version = $11,
input_schema = $12
WHERE uid = $13;
