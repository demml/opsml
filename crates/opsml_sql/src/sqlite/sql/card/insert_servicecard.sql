INSERT INTO opsml_service_registry (
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
    deployment
    ) 
    VALUES 
    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);