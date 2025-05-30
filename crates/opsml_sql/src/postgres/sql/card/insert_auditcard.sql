INSERT INTO opsml_audit_registry (
    uid, 
    app_env, 
    name, 
    space, 
    major, 
    minor, 
    patch, 
    version, 
    tags, 
    approved, 
    datacard_uids, 
    modelcard_uids, 
    experimentcard_uids, 
    pre_tag, 
    build_tag,
    username,
    opsml_version
) 
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17);