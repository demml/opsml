-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_agent_registry (
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
    cards TEXT DEFAULT '[]',
    opsml_version TEXT NOT NULL DEFAULT '0.0.0',
    username TEXT NOT NULL DEFAULT 'guest',
    service_type TEXT NOT NULL DEFAULT 'mcp',
    metadata TEXT,
    deployment TEXT,
    service_config TEXT,
    tags TEXT,
    content_hash BLOB
);

CREATE INDEX idx_opsml_agent_registry_space_name ON opsml_agent_registry (space, name);
ALTER TABLE opsml_prompt_registry ADD COLUMN content_hash BLOB;
ALTER TABLE opsml_mcp_registry ADD COLUMN content_hash BLOB;
ALTER TABLE opsml_service_registry ADD COLUMN content_hash BLOB;