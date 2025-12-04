SELECT 
    *
FROM opsml_experiment_metric 
WHERE experiment_uid = ?
    AND (? IS NULL OR name IN (SELECT value FROM json_each(?)))
    AND (? IS NULL OR is_eval = ?)
ORDER BY name ASC, COALESCE(step, 999999) ASC, created_at ASC