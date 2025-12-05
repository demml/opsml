-- Composite index for main query
CREATE INDEX idx_experiment_metric_query
ON opsml_experiment_metric (experiment_uid, name, step, created_at)
WHERE is_eval IS NOT NULL;

-- Partial index for eval metrics
CREATE INDEX idx_experiment_metric_eval
ON opsml_experiment_metric (experiment_uid, name, step, created_at)
WHERE is_eval = 1;  -- SQLite uses 1/0 for boolean

-- Partial index for non-eval metrics
CREATE INDEX idx_experiment_metric_non_eval
ON opsml_experiment_metric (experiment_uid, name, step, created_at)
WHERE is_eval = 0;  -- SQLite uses 1/0 for boolean

-- Composite index for hardware metrics
CREATE INDEX idx_experiment_hardware_metric_query
ON opsml_experiment_hardware_metric (experiment_uid, created_at);