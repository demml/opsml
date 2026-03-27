UPDATE opsml_audit_registry SET
app_env = ?,
name = ?,
space = ?,
tags = ?,
approved = ?,
datacard_uids = ?,
modelcard_uids = ?,
experimentcard_uids = ?,
username = ?,
opsml_version = ?
WHERE uid = ?
