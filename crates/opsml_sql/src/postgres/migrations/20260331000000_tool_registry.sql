-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_tool_registry (
    uid TEXT NOT NULL PRIMARY KEY,
    space TEXT NOT NULL,
    name TEXT NOT NULL,
    major INTEGER NOT NULL DEFAULT 0,
    minor INTEGER NOT NULL DEFAULT 0,
    patch INTEGER NOT NULL DEFAULT 0,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT NOT NULL,
    tags JSONB NOT NULL DEFAULT '[]',
    app_env TEXT NOT NULL DEFAULT 'dev',
    opsml_version TEXT NOT NULL,
    username TEXT NOT NULL DEFAULT 'guest',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tool_type TEXT NOT NULL DEFAULT 'ShellScript',
    args_schema JSONB,
    content_hash BYTEA,
    download_count BIGINT NOT NULL DEFAULT 0,
    description TEXT
);
CREATE INDEX IF NOT EXISTS idx_tool_space_name ON opsml_tool_registry (space, name);
CREATE INDEX IF NOT EXISTS idx_tool_uid ON opsml_tool_registry (uid);
CREATE INDEX IF NOT EXISTS idx_tool_type ON opsml_tool_registry (tool_type);
CREATE INDEX IF NOT EXISTS idx_tool_download_count ON opsml_tool_registry (download_count DESC);
CREATE UNIQUE INDEX IF NOT EXISTS uq_tool_space_name_version ON opsml_tool_registry (space, name, version);
