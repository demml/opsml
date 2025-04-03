-- Add migration script here
-- MySQL Migration Script

-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_data_registry (
    uid TEXT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_env TEXT DEFAULT 'development',
    name TEXT,
    repository TEXT,
    major INT NOT NULL,
    minor INT NOT NULL,
    patch INT NOT NULL,
    pre_tag TEXT,
    build_tag TEXT,
    version TEXT,
    tags JSON,
    data_type TEXT,
    experimentcard_uid TEXT,
    auditcard_uid TEXT,
    interface_type TEXT NOT NULL DEFAULT 'undefined',
    username TEXT NOT NULL DEFAULT 'guest'
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
    promptcard_uids JSON,
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
CREATE TABLE IF NOT EXISTS opsml_experiment_metric (
    experiment_uid VARCHAR(64),
    name VARCHAR(128),
    value FLOAT,
    step INT,
    timestamp BIGINT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    idx INT PRIMARY KEY AUTO_INCREMENT
);

-- ParameterSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_parameter (
    experiment_uid VARCHAR(64),
    name VARCHAR(128),
    value JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    idx INT PRIMARY KEY AUTO_INCREMENT
);

-- HardwareSchema
CREATE TABLE IF NOT EXISTS opsml_experiment_hardware_metric (
    experiment_uid VARCHAR(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_percent_utilization FLOAT,
    cpu_percent_per_core JSON, -- JSONB is not supported in SQLite, use TEXT to store JSON strings
    free_memory BIGINT,
    total_memory BIGINT,
    used_memory BIGINT,
    available_memory BIGINT,
    used_percent_memory DOUBLE,
    bytes_recv BIGINT,
    bytes_sent BIGINT,
    idx INT AUTO_INCREMENT PRIMARY KEY,
    INDEX idx_experiment_uid (experiment_uid)
);

CREATE TABLE IF NOT EXISTS opsml_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    permissions JSON NOT NULL,
    group_permissions JSON NOT NULL,
    role VARCHAR(32) DEFAULT 'user',
    refresh_token VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS opsml_artifact_key (
    uid VARCHAR(64) PRIMARY KEY,
    registry_type VARCHAR(32),
    encrypted_key VARBINARY(255),
    storage_key VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS opsml_audit_event (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    username TEXT NOT NULL,
    client_ip TEXT NOT NULL,
    user_agent TEXT, 
    operation_type TEXT NOT NULL,  
    resource_type TEXT NOT NULL,   
    resource_id TEXT NOT NULL,              
    access_location TEXT,          
    status TEXT NOT NULL,        
    error_message TEXT,          
    metadata JSON,               
    registry_type TEXT,  
    route TEXT,
    INDEX idx_created_at (created_at)
);

-- DataSchema
CREATE TABLE IF NOT EXISTS opsml_prompt_registry (
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
    experimentcard_uid VARCHAR(64),
    auditcard_uid VARCHAR(64),
    username VARCHAR(255) NOT NULL DEFAULT 'guest'
);