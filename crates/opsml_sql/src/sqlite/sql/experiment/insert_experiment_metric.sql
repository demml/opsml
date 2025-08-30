INSERT INTO opsml_experiment_metric (
    experiment_uid, 
    name, 
    value,
    step,
    timestamp,
    is_eval
) VALUES (?, ?, ?, ?, ?, ?)