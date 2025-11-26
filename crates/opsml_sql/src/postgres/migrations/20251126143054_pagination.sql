-- Optimized composite index for grouped pagination queries

-- Data
CREATE INDEX idx_data_cards_grouped_page
ON opsml_data_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);

-- Model
CREATE INDEX idx_model_cards_grouped_page
ON opsml_model_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);


-- Experiment
CREATE INDEX idx_experiment_cards_grouped_page
ON opsml_experiment_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);

-- Deck
CREATE INDEX idx_service_cards_grouped_page
ON opsml_service_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);

-- prompt
CREATE INDEX idx_prompt_cards_grouped_page
ON opsml_prompt_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);

-- mcp
CREATE INDEX idx_mcp_cards_grouped_page
ON opsml_mcp_registry (space, name, created_at DESC)
INCLUDE (version, uid, tags);