-- add service_type column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN service_type VARCHAR(32) NOT NULL DEFAULT 'api';
-- add metadata column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN metadata JSON;
-- add deployment column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN deployment JSON;
-- add service_config column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN service_config JSON;
-- add tags column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN tags JSON