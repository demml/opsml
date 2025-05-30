UPDATE opsml_audit_registry SET 
app_env = $1, 
name = $2, 
space = $3, 
major = $4, 
minor = $5, 
patch = $6, 
version = $7, 
tags = $8, 
approved = $9, 
datacard_uids = $10, 
modelcard_uids = $11, 
experimentcard_uids = $12, 
pre_tag = $13, 
build_tag = $14,
username = $15,
opsml_version = $16
WHERE uid = $17;