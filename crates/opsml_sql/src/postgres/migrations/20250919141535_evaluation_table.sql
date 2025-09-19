-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_evaluation_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    name TEXT NOT NULL,
    evaluation_type TEXT NOT NULL,
    evaluation_provider TEXT NOT NULL
);

CREATE INDEX idx_opsml_evaluation_registry_name ON opsml_evaluation_registry (name);
CREATE INDEX idx_opsml_evaluation_registry_uid ON opsml_evaluation_registry (uid);