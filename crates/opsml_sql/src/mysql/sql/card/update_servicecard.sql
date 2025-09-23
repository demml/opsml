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
    service_type = ?
WHERE uid = ?;