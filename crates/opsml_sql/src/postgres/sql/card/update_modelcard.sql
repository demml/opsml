UPDATE opsml_model_registry SET 
app_env = $1, 
name = $2, 
space = $3, 
major = $4, 
minor = $5, 
patch = $6, 
version = $7, 
datacard_uid = $8, 
data_type = $9, 
model_type = $10, 
interface_type = $11, 
task_type = $12, 
tags = $13, 
experimentcard_uid = $14, 
auditcard_uid = $15, 
pre_tag = $16, 
build_tag = $17,
username = $18,
opsml_version = $19
WHERE uid = $20;