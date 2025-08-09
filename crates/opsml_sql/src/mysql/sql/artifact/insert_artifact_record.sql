INSERT INTO opsml_artifact_registry (
    uid,
    created_at,
    app_env,
    space,
    name,
    major,
    minor,
    patch,
    pre_tag,
    build_tag,
    version,
    data_type
) VALUES (
    ?, 
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,         
    ?,
    ?,
    ?,
    ?
);