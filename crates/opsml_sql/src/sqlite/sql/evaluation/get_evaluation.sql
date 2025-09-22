SELECT 
    uid,
    app_env,
    name,
    created_at,
    name,
    evaluation_type,
    evaluation_provider
FROM opsml_evaluation_registry WHERE uid = ?;