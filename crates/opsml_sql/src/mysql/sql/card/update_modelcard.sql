UPDATE opsml_model_registry SET
app_env = ?,
name = ?,
space = ?,
datacard_uid = ?,
data_type = ?,
model_type = ?,
interface_type = ?,
task_type = ?,
tags = ?,
experimentcard_uid = ?,
auditcard_uid = ?,
username = ?,
opsml_version = ?
WHERE uid = ?
