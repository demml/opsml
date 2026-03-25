UPDATE opsml_model_registry SET
app_env = $1,
name = $2,
space = $3,
datacard_uid = $4,
data_type = $5,
model_type = $6,
interface_type = $7,
task_type = $8,
tags = $9,
experimentcard_uid = $10,
auditcard_uid = $11,
username = $12,
opsml_version = $13
WHERE uid = $14;
