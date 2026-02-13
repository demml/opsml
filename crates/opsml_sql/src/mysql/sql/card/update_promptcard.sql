UPDATE opsml_prompt_registry SET
app_env = ?,
name = ?,
space = ?,
major = ?,
minor = ?,
patch = ?,
version = ?,
tags = ?,
experimentcard_uid = ?,
auditcard_uid = ?,
pre_tag = ?,
build_tag = ?,
username = ?,
opsml_version = ?
content_hash = ?
WHERE uid = ?;