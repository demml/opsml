INSERT INTO opsml_experiment_metric (
    experiment_uid, 
    name, 
    value,
    step,
    timestamp
) VALUES ($1, $2, $3, $4, $5)