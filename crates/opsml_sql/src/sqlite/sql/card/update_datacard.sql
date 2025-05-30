UPDATE opsml_data_registry SET  
app_env = ?, 
name = ?, 
space = ?, 
major = ?, 
minor = ?, 
patch = ?, 
version = ?, 
data_type = ?, 
interface_type = ?, 
tags = ?, 
experimentcard_uid = ?, 
auditcard_uid = ?, 
pre_tag = ?, 
build_tag = ?,
username = ?,
opsml_version = ?
WHERE uid = ?