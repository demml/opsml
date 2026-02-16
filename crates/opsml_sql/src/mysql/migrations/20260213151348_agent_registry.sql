-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_agent_registry (
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
    cards JSON NOT NULL DEFAULT ('[]'),
    opsml_version VARCHAR(255) NOT NULL DEFAULT '0.0.0',
    username VARCHAR(255) NOT NULL DEFAULT 'guest',
    service_type VARCHAR(32) NOT NULL DEFAULT 'api',
    metadata JSON,
    deployment JSON,
    service_config JSON,
    tags JSON,
    status INTEGER NOT NULL DEFAULT 1,
    content_hash BINARY(32)
);

CREATE INDEX idx_opsml_agent_registry_space_name ON opsml_agent_registry (space, name);

ALTER TABLE opsml_prompt_registry
ADD COLUMN content_hash BINARY(32);

ALTER TABLE opsml_mcp_registry
ADD COLUMN content_hash BINARY(32);

ALTER TABLE opsml_service_registry
ADD COLUMN content_hash BINARY(32);