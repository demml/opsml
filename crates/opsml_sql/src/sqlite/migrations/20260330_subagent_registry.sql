-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_subagent_registry (
    uid TEXT NOT NULL PRIMARY KEY,
    space TEXT NOT NULL,
    name TEXT NOT NULL,
    major INTEGER NOT NULL DEFAULT 0,
    minor INTEGER NOT NULL DEFAULT 0,
    patch INTEGER NOT NULL DEFAULT 0,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    app_env TEXT NOT NULL DEFAULT 'dev',
    opsml_version TEXT NOT NULL,
    username TEXT NOT NULL DEFAULT 'guest',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    compatible_clis TEXT NOT NULL DEFAULT '[]',
    content_hash BLOB,
    download_count INTEGER NOT NULL DEFAULT 0,
    description TEXT
);
CREATE INDEX IF NOT EXISTS idx_subagent_space_name ON opsml_subagent_registry (space, name);
CREATE INDEX IF NOT EXISTS idx_subagent_download_count ON opsml_subagent_registry (download_count DESC);
CREATE UNIQUE INDEX IF NOT EXISTS uq_subagent_space_name_version ON opsml_subagent_registry (space, name, version);
