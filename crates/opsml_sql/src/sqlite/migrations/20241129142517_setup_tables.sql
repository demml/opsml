-- Add migration script here
-- SQLite Migration Script

-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_data_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    contact TEXT,
    tags TEXT,
    data_type TEXT,
    runcard_uid TEXT,
    pipelinecard_uid TEXT,
    auditcard_uid TEXT,
    interface_type TEXT NOT NULL DEFAULT 'undefined'
);

-- ModelSchema
CREATE TABLE IF NOT EXISTS opsml_model_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    contact TEXT,
    tags TEXT,
    datacard_uid TEXT,
    sample_data_type TEXT,
    model_type TEXT,
    runcard_uid TEXT,
    pipelinecard_uid TEXT,
    auditcard_uid TEXT,
    interface_type TEXT NOT NULL DEFAULT 'undefined',
    task_type TEXT NOT NULL DEFAULT 'undefined'
);

-- RunSchema
CREATE TABLE IF NOT EXISTS opsml_run_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    contact TEXT,
    tags TEXT,
    datacard_uids TEXT,
    modelcard_uids TEXT,
    pipelinecard_uid TEXT,
    project TEXT,
    artifact_uris TEXT,
    compute_environment TEXT
);

-- AuditSchema
CREATE TABLE IF NOT EXISTS opsml_audit_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    contact TEXT,
    tags TEXT,
    approved BOOLEAN,
    datacard_uids TEXT,
    modelcard_uids TEXT,
    runcard_uids TEXT
);

-- PipelineSchema
CREATE TABLE IF NOT EXISTS opsml_pipeline_registry (
    uid TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    contact TEXT,
    tags TEXT,
    pipeline_code_uri TEXT,
    datacard_uids TEXT,
    modelcard_uids TEXT,
    runcard_uids TEXT
);

-- ProjectSchema
CREATE TABLE IF NOT EXISTS opsml_project_registry (
    uid TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name TEXT,
    repository TEXT,
    project_id INTEGER PRIMARY KEY,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64)
);

-- MetricSchema
CREATE TABLE IF NOT EXISTS opsml_run_metrics (
    run_uid TEXT,
    name TEXT,
    value REAL,
    step INTEGER,
    timestamp INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    idx INTEGER PRIMARY KEY AUTOINCREMENT
);

-- ParameterSchema
CREATE TABLE IF NOT EXISTS opsml_run_parameters (
    run_uid TEXT,
    name TEXT,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    idx INTEGER PRIMARY KEY AUTOINCREMENT
);

-- HardwareMetricSchema
CREATE TABLE IF NOT EXISTS opsml_run_hardware_metrics (
    run_uid TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cpu_percent_utilization REAL,
    cpu_percent_per_core TEXT, -- JSONB is not supported in SQLite, use TEXT to store JSON strings
    compute_overall REAL,
    compute_utilized REAL,
    load_avg REAL,
    sys_ram_total INTEGER,
    sys_ram_used INTEGER,
    sys_ram_available INTEGER,
    sys_ram_percent_used REAL,
    sys_swap_total INTEGER,
    sys_swap_used INTEGER,
    sys_swap_free INTEGER,
    sys_swap_percent REAL,
    bytes_recv INTEGER,
    bytes_sent INTEGER,
    gpu_percent_utilization REAL,
    gpu_percent_per_core TEXT, -- JSONB is not supported in SQLite, use TEXT to store JSON strings
    idx INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE IF NOT EXISTS opsml_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    permissions TEXT NOT NULL,
    group_permissions TEXT NOT NULL,
    refresh_token TEXT
);