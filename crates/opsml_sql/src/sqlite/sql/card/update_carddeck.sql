UPDATE opsml_deck_registry SET 
    app_env = ?, 
    name = ?, 
    space = ?, 
    major = ?, 
    minor = ?, 
    patch = ?, 
    version = ?, 
    cards = ?,
    username = ?,
    opsml_version = ?
WHERE uid = ?;