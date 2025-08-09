-- Adding artifact_registry table

CREATE TABLE IF NOT EXISTS opsml_artifact_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    app_env TEXT DEFAULT 'development',
    space TEXT NOT NULL, -- the space the file belongs to
    name TEXT NOT NULL, -- the filename, keeping consistency with other tables
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    media_type TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_opsml_artifact_registry_space_name_version ON opsml_artifact_registry (space, name, version, created_at);
CREATE INDEX idx_opsml_artifact_registry_uid ON opsml_artifact_registry (uid);