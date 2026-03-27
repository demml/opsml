UPDATE opsml_experiment_registry SET
app_env = $1,
name = $2,
space = $3,
tags = $4,
datacard_uids = $5,
modelcard_uids = $6,
promptcard_uids = $7,
service_card_uids = $8,
experimentcard_uids = $9,
username = $10,
opsml_version = $11,
status = $12
WHERE uid = $13;
