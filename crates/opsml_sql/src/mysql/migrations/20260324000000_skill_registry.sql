-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_skill_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    space VARCHAR(255),
    name VARCHAR(255),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(255),
    build_tag VARCHAR(255),
    version VARCHAR(255),
    tags JSON,
    compatible_tools JSON NOT NULL,
    dependencies JSON NOT NULL,
    description TEXT,
    license VARCHAR(255),
    content_hash VARBINARY(64),
    opsml_version VARCHAR(255) NOT NULL DEFAULT '0.0.0',
    username VARCHAR(255) NOT NULL DEFAULT 'guest',
    download_count BIGINT NOT NULL DEFAULT 0,
    input_schema JSON
);

CREATE INDEX idx_opsml_skill_registry_space_name ON opsml_skill_registry (space, name);
