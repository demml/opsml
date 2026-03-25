-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_skill_registry (
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
    description TEXT,
    compatible_tools TEXT NOT NULL DEFAULT '[]',
    dependencies TEXT NOT NULL DEFAULT '[]',
    license TEXT,
    content_hash BLOB,
    tags TEXT DEFAULT '[]',
    opsml_version TEXT NOT NULL DEFAULT '0.0.0',
    username TEXT NOT NULL DEFAULT 'guest',
    download_count INTEGER NOT NULL DEFAULT 0,
    input_schema TEXT
);

CREATE INDEX idx_opsml_skill_registry_space_name ON opsml_skill_registry (space, name);
