-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_subagent_registry (
    uid VARCHAR(64) NOT NULL PRIMARY KEY,
    space VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    major INT NOT NULL DEFAULT 0,
    minor INT NOT NULL DEFAULT 0,
    patch INT NOT NULL DEFAULT 0,
    pre_tag VARCHAR(255),
    build_tag VARCHAR(255),
    version VARCHAR(255) NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    app_env VARCHAR(32) NOT NULL DEFAULT 'dev',
    opsml_version VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL DEFAULT 'guest',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    compatible_clis TEXT NOT NULL DEFAULT '[]',
    content_hash VARBINARY(64),
    download_count BIGINT NOT NULL DEFAULT 0,
    description TEXT
);
CREATE INDEX idx_subagent_space_name ON opsml_subagent_registry (space, name);
CREATE INDEX idx_subagent_download_count ON opsml_subagent_registry (download_count DESC);
CREATE UNIQUE INDEX uq_subagent_space_name_version ON opsml_subagent_registry (space, name, version);
