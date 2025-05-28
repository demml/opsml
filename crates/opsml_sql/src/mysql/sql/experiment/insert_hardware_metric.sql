INSERT INTO opsml_experiment_hardware_metric (
    experiment_uid,
    created_at,
    cpu_percent_utilization,
    cpu_percent_per_core,
    free_memory,
    total_memory,
    used_memory,
    available_memory,
    used_percent_memory,
    bytes_recv,
    bytes_sent
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);