-- Add migration script here
-- MySQL Migration Script

-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_data_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags JSON,
    data_type VARCHAR(64),
    experimentcard_uid VARCHAR(64),
    auditcard_uid VARCHAR(64),
    interface_type VARCHAR(64) NOT NULL DEFAULT 'undefined',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- ModelSchema
CREATE TABLE IF NOT EXISTS opsml_model_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags JSON,
    datacard_uid VARCHAR(64),
    data_type VARCHAR(64),
    model_type VARCHAR(64),
    experimentcard_uid VARCHAR(64),
    auditcard_uid VARCHAR(64),
    interface_type VARCHAR(64) NOT NULL DEFAULT 'undefined',
    task_type VARCHAR(64) NOT NULL DEFAULT 'undefined',
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- RunSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags JSON,
    datacard_uids JSON,
    modelcard_uids JSON,
    experimentcard_uids JSON,
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- AuditSchema
CREATE TABLE IF NOT EXISTS opsml_audit_registry (
    uid VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env VARCHAR(32) DEFAULT 'development',
    name VARCHAR(128),
    repository VARCHAR(128),
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag VARCHAR(16),
    build_tag VARCHAR(16),
    version VARCHAR(64),
    tags JSON,
    approved BOOLEAN,
    datacard_uids JSON,
    modelcard_uids JSON,
    experimentcard_uids JSON,
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);

-- MetricSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_metrics (
    experiment_uid VARCHAR(64),
    name VARCHAR(128),
    value FLOAT,
    step INT,
    timestamp BIGINT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    idx INT PRIMARY KEY AUTO_INCREMENT
);

-- ParameterSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_parameters (
    experiment_uid VARCHAR(64),
    name VARCHAR(128),
    value VARCHAR(128),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    idx INT PRIMARY KEY AUTO_INCREMENT
);

-- HardwareSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_hardware_metrics (
    experiment_uid VARCHAR(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_percent_utilization FLOAT,
    cpu_percent_per_core JSON, -- JSONB is not supported in SQLite, use TEXT to store JSON strings
    free_memory INT,
    total_memory INT,
    used_memory INT,
    available_memory INT,
    used_percent_memory FLOAT,
    bytes_recv FLOAT,
    bytes_sent FLOAT,
    idx INT AUTO_INCREMENT PRIMARY KEY,
    INDEX idx_experiment_uid (experiment_uid)
);

CREATE TABLE IF NOT EXISTS opsml_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    permissions JSON NOT NULL,
    group_permissions JSON NOT NULL,
    refresh_token VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS opsml_artifact_key (
    uid VARCHAR(64) PRIMARY KEY,
    registry_type VARCHAR(32),
    encrypted_key VARBINARY(255),
    storage_key VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS opsml_operations (
    username VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    access_type VARCHAR(16) NOT NULL,
    access_location VARCHAR(255) NOT NULL,
    INDEX idx_created_at (created_at)
);