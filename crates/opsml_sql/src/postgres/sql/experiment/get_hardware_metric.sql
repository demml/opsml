SELECT 
    *
FROM opsml_experiment_hardware_metric 
WHERE experiment_uid = $1
ORDER BY created_at ASC