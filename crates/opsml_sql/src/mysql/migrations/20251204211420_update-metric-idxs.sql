-- Composite index for main query (includes is_eval for filtering)
CREATE INDEX idx_experiment_metric_query
ON opsml_experiment_metric (experiment_uid, is_eval, name, step, created_at);

-- Composite index for hardware metrics
CREATE INDEX idx_experiment_hardware_metric_query
ON opsml_experiment_hardware_metric (experiment_uid, created_at);