UPDATE opsml_prompt_registry SET
app_env = ?,
name = ?,
space = ?,
tags = ?,
experimentcard_uid = ?,
auditcard_uid = ?,
username = ?,
opsml_version = ?,
content_hash = ?
WHERE uid = ?;
