SELECT 
    *
FROM opsml_experiment_metric 
WHERE experiment_uid = ?
    AND (? IS NULL OR FIND_IN_SET(name, ?))
    AND (? IS NULL OR is_eval = ?)
ORDER BY name ASC, COALESCE(step, 999999) ASC, created_at ASC