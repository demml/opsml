SELECT 
    COALESCE((SELECT COUNT(uid) FROM opsml_model_registry WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)), 0) AS recent_models,
    COALESCE((SELECT COUNT(uid) FROM opsml_data_registry WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)), 0) AS recent_data,
    COALESCE((SELECT COUNT(uid) FROM opsml_prompt_registry WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)), 0) AS recent_prompts,
    COALESCE((SELECT COUNT(uid) FROM opsml_experiment_registry WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)), 0) AS recent_experiments;