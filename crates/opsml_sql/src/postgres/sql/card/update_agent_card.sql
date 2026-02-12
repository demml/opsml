UPDATE opsml_mcp_registry SET
app_env = $1,
space = $2,
name = $3,
major = $4,
minor = $5,
patch = $6,
version = $7,
username = $8,
opsml_version = $9,
promptcard_uids = $10,
tags = $11
WHERE uid = $12;