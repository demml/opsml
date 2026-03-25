UPDATE opsml_audit_registry SET
app_env = $1,
name = $2,
space = $3,
tags = $4,
approved = $5,
datacard_uids = $6,
modelcard_uids = $7,
experimentcard_uids = $8,
username = $9,
opsml_version = $10
WHERE uid = $11;
