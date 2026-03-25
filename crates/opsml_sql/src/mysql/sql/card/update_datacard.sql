UPDATE opsml_data_registry SET
app_env = ?,
name = ?,
space = ?,
data_type = ?,
interface_type = ?,
tags = ?,
experimentcard_uid = ?,
auditcard_uid = ?,
username = ?,
opsml_version = ?
WHERE uid = ?
