SELECT 
    *
FROM opsml_experiment_hardware_metric 
WHERE experiment_uid = ?
ORDER BY created_at ASC