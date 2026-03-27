UPDATE opsml_data_registry SET
app_env = $1,
name = $2,
space = $3,
data_type = $4,
interface_type = $5,
tags = $6,
experimentcard_uid = $7,
auditcard_uid = $8,
username = $9,
opsml_version = $10
WHERE uid = $11;
