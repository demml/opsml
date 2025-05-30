SELECT 
    space,
    CAST(SUM(CASE WHEN registry_type = 'model' THEN 1 ELSE 0 END) AS SIGNED) as model_count,
    CAST(SUM(CASE WHEN registry_type = 'data' THEN 1 ELSE 0 END) AS SIGNED) as data_count,
    CAST(SUM(CASE WHEN registry_type = 'prompt' THEN 1 ELSE 0 END) AS SIGNED) as prompt_count,
    CAST(SUM(CASE WHEN registry_type = 'experiment' THEN 1 ELSE 0 END) AS SIGNED) as experiment_count
FROM opsml_space_name
GROUP BY space;