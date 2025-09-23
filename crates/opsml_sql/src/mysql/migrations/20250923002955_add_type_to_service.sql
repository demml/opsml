-- add service_type column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN IF NOT EXISTS service_type TEXT NOT NULL DEFAULT 'api';
