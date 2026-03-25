UPDATE opsml_experiment_registry SET
app_env = ?,
name = ?,
space = ?,
tags = ?,
datacard_uids = ?,
modelcard_uids = ?,
promptcard_uids = ?,
service_card_uids = ?,
experimentcard_uids = ?,
username = ?,
opsml_version = ?,
status = ?
WHERE uid = ?
