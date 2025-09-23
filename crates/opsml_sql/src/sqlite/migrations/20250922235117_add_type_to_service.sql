-- Add service_type, metadata and deployment column to opsml_service_registry table
ALTER TABLE opsml_service_registry ADD COLUMN service_type TEXT NOT NULL DEFAULT 'api';
ALTER TABLE opsml_service_registry ADD COLUMN metadata TEXT;
ALTER TABLE opsml_service_registry ADD COLUMN deployment TEXT;
ALTER TABLE opsml_service_registry ADD COLUMN service_config TEXT;
ALTER TABLE opsml_service_registry ADD COLUMN tags TEXT;

