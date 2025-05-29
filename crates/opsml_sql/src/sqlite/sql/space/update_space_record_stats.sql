WITH space_stats AS (
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
    )


    , SPACE_STATS_WITH_USERS AS (
        SELECT 
            ss.space,
            ss.experiment_count,
            ss.model_count,
            ss.data_count,
            ss.prompt_count,
            COALESCE(su.user_count, 0) as user_count
        FROM space_stats ss
        LEFT JOIN SPACE_USER_COUNT su ON ss.space = su.space
    )
INSERT INTO opsml_space (
    space,
    data_count,
    model_count,
    experiment_count,
    prompt_count,
    user_count,
    updated_at
)
VALUES (
    (SELECT space FROM SPACE_STATS_WITH_USERS),
    (SELECT data_count FROM SPACE_STATS_WITH_USERS),
    (SELECT model_count FROM SPACE_STATS_WITH_USERS),
    (SELECT experiment_count FROM SPACE_STATS_WITH_USERS),
    (SELECT prompt_count FROM SPACE_STATS_WITH_USERS),
    (SELECT user_count FROM SPACE_STATS_WITH_USERS),
    CURRENT_TIMESTAMP
)
ON CONFLICT(space) DO UPDATE SET
    data_count = excluded.data_count,
    model_count = excluded.model_count,
    experiment_count = excluded.experiment_count,
    prompt_count = excluded.prompt_count,
    user_count = excluded.user_count,
    updated_at = CURRENT_TIMESTAMP;