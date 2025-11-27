-- Add generic status column to all registries. This follows (0,1,2,3)
-- 0: inactive
-- 1: ok
-- 2: error
-- 3: active

-- MySQL 8.0.29+ supports IF NOT EXISTS
ALTER TABLE opsml_data_registry ADD COLUMN status TINYINT NOT NULL DEFAULT 1;
ALTER TABLE opsml_model_registry ADD COLUMN status TINYINT NOT NULL DEFAULT 1;
ALTER TABLE opsml_experiment_registry ADD COLUMN status TINYINT NOT NULL DEFAULT 1;
ALTER TABLE opsml_prompt_registry ADD COLUMN status TINYINT NOT NULL DEFAULT 1;
ALTER TABLE opsml_mcp_registry ADD COLUMN status TINYINT NOT NULL DEFAULT 1;
ALTER TABLE opsml_service_registry ADD COLUMN status TINYINT NOT NULL DEFAULT 1;