INSERT INTO opsml_skill_registry (
uid,
app_env,
name,
space,
major,
minor,
patch,
version,
pre_tag,
build_tag,
tags,
compatible_tools,
dependencies,
description,
license,
content_hash,
username,
opsml_version,
input_schema
)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19);
