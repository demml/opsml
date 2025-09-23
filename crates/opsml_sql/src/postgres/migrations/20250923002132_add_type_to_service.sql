-- add service_type column to service cards
ALTER TABLE opsml_service_registry ADD COLUMN IF NOT EXISTS service_type TEXT NOT NULL DEFAULT 'api';

CREATE INDEX idx_opsml_service_registry_service_type ON opsml_service_registry (service_type);