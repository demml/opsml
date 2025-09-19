-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_evaluation_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(255),
    evaluation_type VARCHAR(255),
    evaluation_provider VARCHAR(255)
);
