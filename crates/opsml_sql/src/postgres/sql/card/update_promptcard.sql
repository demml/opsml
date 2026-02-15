UPDATE opsml_prompt_registry SET
app_env = $1,
name = $2,
space = $3,
major = $4,
minor = $5,
patch = $6,
version = $7,
tags = $8,
experimentcard_uid = $9,
auditcard_uid = $10,
pre_tag = $11,
build_tag = $12,
username = $13,
opsml_version = $14,
content_hash = $15
WHERE uid = $16;