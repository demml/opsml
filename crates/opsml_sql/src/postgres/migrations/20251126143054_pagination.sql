-- Optimized composite index for grouped pagination queries

-- Data
CREATE INDEX CONCURRENTLY idx_cards_grouped_page
ON opsml_data_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);

-- Model
CREATE INDEX CONCURRENTLY idx_cards_grouped_page
ON opsml_model_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);


-- Experiment
CREATE INDEX CONCURRENTLY idx_cards_grouped_page
ON opsml_experiment_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);

-- Deck
CREATE INDEX CONCURRENTLY idx_cards_grouped_page
ON opsml_deck_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);

-- prompt
CREATE INDEX CONCURRENTLY idx_cards_grouped_page
ON opsml_prompt_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);

-- mcp
CREATE INDEX CONCURRENTLY idx_cards_grouped_page
ON opsml_mcp_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);