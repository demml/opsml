UPDATE opsml_service_registry SET 
    app_env = ?, 
    name = ?, 
    space = ?, 
    major = ?, 
    minor = ?, 
    patch = ?, 
    version = ?, 
    cards = ?,
    username = ?,
    opsml_version = ?,
    service_type = ?,
    metadata = ?,
    deployment = ?,
    service_config = ?
WHERE uid = ?;