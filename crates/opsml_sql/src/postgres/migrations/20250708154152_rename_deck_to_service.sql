-- Rename card deck to service card in the database schema
ALTER TABLE opsml_deck_registry RENAME TO opsml_service_registry;

-- Update associated indexes
ALTER INDEX idx_opsml_deck_registry_space_name_version RENAME TO idx_opsml_service_registry_space_name_version;
ALTER INDEX idx_opsml_deck_registry_uid RENAME TO idx_opsml_service_registry_uid;

-- Rename the column in experiment registry
ALTER TABLE opsml_experiment_registry 
RENAME COLUMN card_deck_uids TO service_card_uids;