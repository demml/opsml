-- add service_type column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN IF NOT EXISTS service_type TEXT NOT NULL DEFAULT 'api';
-- add metadata column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN IF NOT EXISTS metadata JSON;
-- add deployment column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN IF NOT EXISTS deployment JSON;
-- add service_config column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN IF NOT EXISTS service_config JSON;
-- add tags column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN IF NOT EXISTS tags JSON;