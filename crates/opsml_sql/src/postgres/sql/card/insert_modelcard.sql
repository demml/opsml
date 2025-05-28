INSERT INTO opsml_model_registry (
    uid, 
    app_env, 
    name, 
    space, 
    major, 
    minor, 
    patch, 
    version, 
    datacard_uid, 
    data_type, 
    model_type, 
    interface_type, 
    task_type, 
    tags, 
    experimentcard_uid, 
    auditcard_uid, 
    pre_tag, 
    build_tag,
    username,
    opsml_version
) 
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20);