-- Add migration script here
CREATE TABLE IF NOT EXISTS opsml_agent_registry (
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
    cards JSONB NOT NULL DEFAULT '[]',
    opsml_version TEXT NOT NULL DEFAULT '0.0.0',
    username TEXT NOT NULL DEFAULT 'guest',
    service_type TEXT NOT NULL DEFAULT 'agent',
    metadata JSONB,
    deployment JSONB,
    service_config JSONB,
    tags JSONB DEFAULT '[]',
    promptcard_uids JSONB DEFAULT '[]'
);

CREATE INDEX idx_opsml_agent_registry_space_name ON opsml_agent_registry (space, name);
CREATE INDEX idx_opsml_agent_registry_uid ON opsml_agent_registry (uid);