SELECT 
    *
FROM opsml_experiment_metric 
WHERE experiment_uid = $1
    AND (CARDINALITY($2::text[]) = 0 OR name = ANY($2::text[]))
    AND ($3::boolean IS NULL OR is_eval = $3)
ORDER BY name ASC, step ASC NULLS LAST, created_at ASC