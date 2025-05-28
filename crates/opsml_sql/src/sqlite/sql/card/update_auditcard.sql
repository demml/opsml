UPDATE opsml_audit_registry SET 
app_env = ?, 
name = ?, 
space = ?, 
major = ?, 
minor = ?, 
patch = ?, 
version = ?, 
tags = ?, 
approved = ?, 
datacard_uids = ?, 
modelcard_uids = ?, 
experimentcard_uids = ?, 
pre_tag = ?, 
build_tag = ?,
username = ?,
opsml_version = ?
WHERE uid = ?