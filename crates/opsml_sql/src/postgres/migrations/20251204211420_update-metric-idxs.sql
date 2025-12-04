-- Add migration script here
CREATE INDEX idx_experiment_metric_query
ON opsml_experiment_metric (experiment_uid, name, step, created_at)
WHERE is_eval IS NOT NULL;

-- Partial index for eval metrics specifically
CREATE INDEX idx_experiment_metric_eval
ON opsml_experiment_metric (experiment_uid, name, step, created_at)
WHERE is_eval = true;

-- Partial index for non-eval metrics
CREATE INDEX idx_experiment_metric_non_eval
ON opsml_experiment_metric (experiment_uid, name, step, created_at)
WHERE is_eval = false;

-- Composite index for filtering and sorting
CREATE INDEX idx_experiment_hardware_metric_query
ON opsml_experiment_hardware_metric (experiment_uid, created_at ASC);