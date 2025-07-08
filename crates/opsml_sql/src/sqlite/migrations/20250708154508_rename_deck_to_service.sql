-- Rename card deck to service card in the database schema
ALTER TABLE opsml_deck_registry RENAME TO opsml_service_registry;

-- Rename the column in experiment registry
ALTER TABLE opsml_experiment_registry RENAME COLUMN card_deck_uids TO service_card_uids;