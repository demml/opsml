UPDATE opsml_prompt_registry SET
app_env = $1,
name = $2,
space = $3,
tags = $4,
experimentcard_uid = $5,
auditcard_uid = $6,
username = $7,
opsml_version = $8,
content_hash = $9
WHERE uid = $10;
