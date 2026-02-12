INSERT INTO opsml_agent_registry (
    uid,
    app_env,
    name,
    space,
    major,
    minor,
    patch,
    version,
    pre_tag,
    build_tag,
    username TEXT NOT NULL DEFAULT 'guest',
    service_type TEXT NOT NULL DEFAULT 'agent',
    metadata JSONB,
    deployment JSONB,
    service_config JSONB,
    tags JSONB DEFAULT '[]',
    promptcard_uids JSONB DEFAULT '[]'
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14);