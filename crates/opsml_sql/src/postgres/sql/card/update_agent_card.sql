UPDATE opsml_mcp_registry SET 
app_env = $1, 
name = $2,
space = $3,
major = $4, 
minor = $5,
patch = $6, 
version = $7, 
cards = $8,
username = $9,
opsml_version = $10,
service_type = $11,
metadata = $12,
deployment = $13,
service_config = $14,
tags = $15,
promptcard_uids = $16
WHERE uid = $17;