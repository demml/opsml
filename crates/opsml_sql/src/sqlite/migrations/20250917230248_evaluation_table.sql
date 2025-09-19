-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_evaluation_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    evaluation_type TEXT,
    evaluation_provider TEXT
);