SELECT 
    space,
    SUM(CASE WHEN registry_type = 'model' THEN 1 ELSE 0 END) as model_count,
    SUM(CASE WHEN registry_type = 'data' THEN 1 ELSE 0 END) as data_count,
    SUM(CASE WHEN registry_type = 'prompt' THEN 1 ELSE 0 END) as prompt_count,
    SUM(CASE WHEN registry_type = 'experiment' THEN 1 ELSE 0 END) as experiment_count
FROM opsml_space_name
GROUP BY space;

