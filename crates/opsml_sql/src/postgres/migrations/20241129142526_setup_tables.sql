-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_data_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    contact VARCHAR(64),
    tags JSONB DEFAULT '[]',
    data_type VARCHAR(64),
    runcard_uid VARCHAR(64),
    pipelinecard_uid VARCHAR(64),
    auditcard_uid VARCHAR(64),
    interface_type VARCHAR(64) NOT NULL DEFAULT 'undefined',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- ModelSchema
CREATE TABLE IF NOT EXISTS opsml_model_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    contact VARCHAR(64),
    tags JSONB DEFAULT '[]',
    datacard_uid VARCHAR(64),
    data_type VARCHAR(64),
    model_type VARCHAR(64),
    runcard_uid VARCHAR(64),
    pipelinecard_uid VARCHAR(64),
    auditcard_uid VARCHAR(64),
    interface_type VARCHAR(64) NOT NULL DEFAULT 'undefined',
    task_type VARCHAR(64) NOT NULL DEFAULT 'undefined',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- RunSchema
CREATE TABLE IF NOT EXISTS opsml_run_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    contact VARCHAR(64),
    tags JSONB DEFAULT '[]',
    datacard_uids JSONB,
    modelcard_uids JSONB,
    pipelinecard_uid VARCHAR(64),
    project VARCHAR(64),
    artifact_uris JSONB,
    compute_environment JSONB,
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- AuditSchema
CREATE TABLE IF NOT EXISTS opsml_audit_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    contact VARCHAR(64),
    tags JSONB DEFAULT '[]',
    approved BOOLEAN,
    datacard_uids JSONB,
    modelcard_uids JSONB,
    runcard_uids JSONB NOT NULL DEFAULT '{}',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- PipelineSchema
CREATE TABLE IF NOT EXISTS opsml_pipeline_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    contact VARCHAR(64),
    tags JSONB DEFAULT '[]',
    pipeline_code_uri VARCHAR(256),
    datacard_uids JSONB,
    modelcard_uids JSONB,
    runcard_uids JSONB,
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- ProjectSchema
CREATE TABLE IF NOT EXISTS opsml_project_registry (
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    uid VARCHAR(64),
    name VARCHAR(128),
    repository VARCHAR(128),
    project_id SERIAL PRIMARY KEY,
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- MetricSchema
CREATE TABLE IF NOT EXISTS opsml_run_metrics (
    run_uid VARCHAR(64),
    name VARCHAR(128),
    value FLOAT,
    step INT,
    timestamp BIGINT,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    idx SERIAL PRIMARY KEY
);

-- ParameterSchema
CREATE TABLE IF NOT EXISTS opsml_run_parameters (
    run_uid VARCHAR(64),
    name VARCHAR(128),
    value VARCHAR(128),
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    idx SERIAL PRIMARY KEY
);

-- HardwareMetricSchema
CREATE TABLE IF NOT EXISTS opsml_run_hardware_metrics (
    run_uid VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    cpu_percent_utilization FLOAT,
    cpu_percent_per_core JSONB,
    compute_overall FLOAT,
    compute_utilized FLOAT,
    load_avg FLOAT,
    sys_ram_total INT,
    sys_ram_used INT,
    sys_ram_available  INT,
    sys_ram_percent_used FLOAT,
    sys_swap_total INT,
    sys_swap_used INT,
    sys_swap_free INT,
    sys_swap_percent FLOAT,
    bytes_recv INT,
    bytes_sent INT,
    gpu_percent_utilization FLOAT,
    gpu_percent_per_core JSONB,
    idx SERIAL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS opsml_users (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    active BOOLEAN DEFAULT TRUE,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    permissions JSONB NOT NULL,
    group_permissions JSONB NOT NULL,
    refresh_token VARCHAR(255)

);

  
CREATE TABLE IF NOT EXISTS opsml_artifact_key (
    uid VARCHAR(64) PRIMARY KEY,
    card_type VARCHAR(32),
    encrypt_key BYTEA,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW()))
);

CREATE TABLE IF NOT EXISTS opsml_operations (
    id SERIAL PRIMARY KEY,
    user VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT (TIMEZONE('utc', NOW())),
    access_type VARCHAR(16) NOT NULL,
    access_location VARCHAR(255) NOT NULL
);