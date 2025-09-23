-- add service_type column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN IF NOT EXISTS service_type TEXT NOT NULL DEFAULT 'api';
-- add metadata column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN IF NOT EXISTS metadata JSONB;
-- add deployment column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN IF NOT EXISTS deployment JSONB;

CREATE INDEX idx_opsml_service_registry_space_name_service_type ON opsml_service_registry (space, name, service_type);