INSERT INTO opsml_experiment_registry (
    uid, 
    app_env, 
    name, 
    space, 
    major, 
    minor, 
    patch, 
    version,
    tags, 
    datacard_uids,
    modelcard_uids, 
    promptcard_uids,
    card_deck_uids,
    experimentcard_uids,
    pre_tag, 
    build_tag,
    username,
    opsml_version
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)