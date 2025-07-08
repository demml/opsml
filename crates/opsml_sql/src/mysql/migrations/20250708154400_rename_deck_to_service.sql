-- Rename card deck to service card in the database schema
RENAME TABLE opsml_deck_registry TO opsml_service_registry;

-- Rename the column in experiment registry
ALTER TABLE opsml_experiment_registry 
CHANGE COLUMN card_deck_uids service_card_uids JSON NOT NULL DEFAULT ('[]');