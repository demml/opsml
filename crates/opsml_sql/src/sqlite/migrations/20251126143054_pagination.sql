-- Optimized composite index for grouped pagination queries

-- Data
CREATE INDEX IF NOT EXISTS idx_data_cards_grouped_page
ON opsml_data_registry(space, name, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_data_cards_tags
ON opsml_data_registry(space, name)
WHERE json_type(tags) = 'array';


-- Model
CREATE INDEX IF NOT EXISTS idx_model_cards_grouped_page
ON opsml_model_registry(space, name, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_model_cards_tags
ON opsml_model_registry(space, name)
WHERE json_type(tags) = 'array';

-- Experiment
CREATE INDEX IF NOT EXISTS idx_experiment_cards_grouped_page
ON opsml_experiment_registry(space, name, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_experiment_cards_tags
ON opsml_experiment_registry(space, name)
WHERE json_type(tags) = 'array';

-- Deck
CREATE INDEX IF NOT EXISTS idx_service_cards_grouped_page
ON opsml_service_registry(space, name, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_service_cards_tags
ON opsml_service_registry(space, name)
WHERE json_type(tags) = 'array';

-- prompt
CREATE INDEX IF NOT EXISTS idx_prompt_cards_grouped_page
ON opsml_prompt_registry(space, name, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_prompt_cards_tags
ON opsml_prompt_registry(space, name)
WHERE json_type(tags) = 'array';

-- mcp
CREATE INDEX IF NOT EXISTS idx_mcp_cards_grouped_page
ON opsml_mcp_registry(space, name, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_mcp_cards_tags
ON opsml_mcp_registry(space, name)
WHERE json_type(tags) = 'array';