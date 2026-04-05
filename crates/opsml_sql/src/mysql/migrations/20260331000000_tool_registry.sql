-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_tool_registry (
    uid VARCHAR(64) NOT NULL PRIMARY KEY,
    space VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    major INT NOT NULL DEFAULT 0,
    minor INT NOT NULL DEFAULT 0,
    patch INT NOT NULL DEFAULT 0,
    pre_tag VARCHAR(255),
    build_tag VARCHAR(255),
    version VARCHAR(255) NOT NULL,
    tags JSON NOT NULL DEFAULT ('[]'),
    app_env VARCHAR(32) NOT NULL DEFAULT 'dev',
    opsml_version VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL DEFAULT 'guest',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tool_type VARCHAR(255) NOT NULL DEFAULT 'ShellScript',
    args_schema JSON,
    content_hash VARBINARY(64),
    download_count BIGINT NOT NULL DEFAULT 0,
    description TEXT
);
CREATE INDEX idx_tool_space_name ON opsml_tool_registry (space, name);
CREATE INDEX idx_tool_type ON opsml_tool_registry (tool_type);
CREATE INDEX idx_tool_download_count ON opsml_tool_registry (download_count DESC);
CREATE UNIQUE INDEX uq_tool_space_name_version ON opsml_tool_registry (space, name, version);
