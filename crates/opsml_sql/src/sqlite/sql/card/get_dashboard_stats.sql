SELECT 
    COALESCE((SELECT COUNT(uid) FROM opsml_model_registry WHERE created_at >= datetime('now', '-7 days')), 0) AS nbr_models,
    COALESCE((SELECT COUNT(uid) FROM opsml_data_registry WHERE created_at >= datetime('now', '-7 days')), 0) AS nbr_data,
    COALESCE((SELECT COUNT(uid) FROM opsml_prompt_registry WHERE created_at >= datetime('now', '-7 days')), 0) AS nbr_prompts,
    COALESCE((SELECT COUNT(uid) FROM opsml_experiment_registry WHERE created_at >= datetime('now', '-7 days')), 0) AS nbr_experiments;