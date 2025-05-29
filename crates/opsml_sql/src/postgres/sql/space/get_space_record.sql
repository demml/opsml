SELECT 
    space,
    description,
    experiment_count,
    model_count,
    data_count,
    prompt_count,
    user_count
FROM opsml_space
WHERE space = $1;