-- Add service_type column to opsml_service_registry table
ALTER TABLE opsml_service_registry ADD COLUMN service_type TEXT NOT NULL DEFAULT 'api';
