INSERT INTO opsml_mcp_registry (
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
    cards, 
    username, 
    opsml_version,
    service_type,
    metadata,
    deployment,
    service_config,
    tags
    ) 
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18);