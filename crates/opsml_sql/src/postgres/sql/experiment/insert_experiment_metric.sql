INSERT INTO opsml_experiment_metric (
    experiment_uid, 
    name, 
    value,
    step,
    timestamp,
    is_eval
) VALUES ($1, $2, $3, $4, $5, $6)