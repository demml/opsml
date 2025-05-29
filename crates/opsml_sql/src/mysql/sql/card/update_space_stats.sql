INSERT INTO opsml_space (
    space,
    data_count,
    model_count,
    experiment_count,
    prompt_count,
    user_count,
    updated_at
)	
WITH 
    SPACE_STATS AS (
        SELECT 
            space,
            SUM(experiment_count) as experiment_count,
            SUM(model_count) as model_count,
            SUM(data_count) as data_count,
            SUM(prompt_count) as prompt_count
        FROM (
            SELECT 
                space,
                COUNT(DISTINCT name) as experiment_count,
                0 as model_count,
                0 as data_count,
                0 as prompt_count
            FROM opsml_experiment_registry
            WHERE space = ?
            GROUP BY space
            UNION ALL
            SELECT
                space,
                0 as experiment_count,
                COUNT(DISTINCT name) as model_count,
                0 as data_count,
                0 as prompt_count
            FROM opsml_model_registry
            WHERE space = ?
            GROUP BY space
            UNION ALL
            SELECT 
                space,
                0 as experiment_count,
                0 as model_count,
                COUNT(DISTINCT name) as data_count,
                0 as prompt_count
            FROM opsml_data_registry
            WHERE space = ?
            GROUP BY space
            UNION ALL
            SELECT
                space,
                0 as experiment_count,
                0 as model_count,
                0 as data_count,
                COUNT(DISTINCT name) as prompt_count
            FROM opsml_prompt_registry
            WHERE space = ?
            GROUP BY space
        
        ) AS combined_spaces
        GROUP BY space
    ),

    SPACE_USER_COUNT AS (
        SELECT 
            space,
            COUNT(DISTINCT username) AS user_count
        FROM (
            SELECT DISTINCT username, space 
            FROM opsml_experiment_registry
            WHERE space = ?
            UNION ALL
            SELECT DISTINCT username, space
            FROM opsml_model_registry 
            WHERE space = ?
            UNION ALL
            SELECT DISTINCT username, space
            FROM opsml_data_registry
            WHERE space = ?
            UNION ALL
            SELECT DISTINCT username, space 
            FROM opsml_prompt_registry
            WHERE space = ?
        ) AS combined_users
        GROUP BY space
    ), 

    SPACE_STATS_WITH_USERS AS (
        SELECT 
            ss.space,
            ss.experiment_count,
            ss.model_count,
            ss.data_count,
            ss.prompt_count,
            COALESCE(su.user_count, 0) as user_count
        FROM SPACE_STATS ss
        LEFT JOIN SPACE_USER_COUNT su ON ss.space = su.space
    )

SELECT 
    space,
    data_count,
    model_count,
    experiment_count,
    prompt_count,
    user_count,
    CURRENT_TIMESTAMP
FROM SPACE_STATS_WITH_USERS as stats
ON DUPLICATE KEY UPDATE
    experiment_count = stats.experiment_count,
    model_count = stats.model_count,
    data_count = stats.data_count,
    prompt_count = stats.prompt_count,
    user_count = stats.user_count,
    updated_at = CURRENT_TIMESTAMP;