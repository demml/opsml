UPDATE opsml_data_registry SET  
app_env = $1, 
name = $2, 
space = $3, 
major = $4, 
minor = $5, 
patch = $6, 
version = $7, 
data_type = $8, 
interface_type = $9, 
tags = $10, 
experimentcard_uid = $11, 
auditcard_uid = $12, 
pre_tag = $13, 
build_tag = $14,
username = $15,
opsml_version = $16
WHERE uid = $17;