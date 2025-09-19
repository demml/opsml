INSERT INTO opsml_evaluation_registry (
    uid, 
    app_env,
    name,
    evaluation_type,
    evaluation_provider
) 
VALUES ($1, $2, $3, $4, $5);