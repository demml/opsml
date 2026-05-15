from .shared.setup import (
    APP_NAME,
    AgentConfig,
    AttachedEval,
    PromptSpec,
    TransportConfig,
    get_shared_config,
    teardown,
)

get_agent_config = get_shared_config

__all__ = [
    "APP_NAME",
    "AgentConfig",
    "AttachedEval",
    "PromptSpec",
    "TransportConfig",
    "get_agent_config",
    "get_shared_config",
    "teardown",
]
