-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_skill_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    space TEXT,
    name TEXT,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    tags JSONB DEFAULT '[]',
    compatible_tools JSONB NOT NULL DEFAULT '[]',
    dependencies JSONB NOT NULL DEFAULT '[]',
    description TEXT,
    license TEXT,
    content_hash BYTEA,
    opsml_version TEXT NOT NULL DEFAULT '0.0.0',
    username TEXT NOT NULL DEFAULT 'guest',
    download_count BIGINT NOT NULL DEFAULT 0,
    input_schema TEXT
);

CREATE INDEX idx_opsml_skill_registry_space_name ON opsml_skill_registry (space, name);
CREATE INDEX idx_opsml_skill_registry_uid ON opsml_skill_registry (uid);
