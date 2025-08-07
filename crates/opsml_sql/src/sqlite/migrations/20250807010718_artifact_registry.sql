CREATE TABLE IF NOT EXISTS opsml_artifact_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    space TEXT,
    name TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    filename TEXT,
    data_type TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);