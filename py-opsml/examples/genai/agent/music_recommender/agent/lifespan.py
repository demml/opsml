from pathlib import Path
from typing import cast

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from opsml import PromptCard
from opsml.app import AppState
from opsml.scouter.tracing import GrpcSpanExporter, BatchConfig


class LifespanConfig(BaseSettings):
    """Configuration for the agent's lifespan events."""

    model_config = SettingsConfigDict(env_prefix="AGENT_LIFESPAN_")

    app_path: Path = Path("opsml_service")


class Prompts(BaseModel):
    """Holds the prompts used by the agent."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    pattern: PromptCard
    preference: PromptCard
    recommendation: PromptCard
    search: PromptCard


config = LifespanConfig()


def get_app_state() -> tuple[AppState, Prompts]:
    """Helper function to load the AppState for the agent."""
    app = AppState.from_path(path=config.app_path)
    service = app.service
    assert service is not None, f"Service config not found in app at {config.app_path}"

    # instrument with Scouter tracing for monitoring and evaluation of lifespan events
    app.instrument(
        exporter=GrpcSpanExporter(),
        batch_config=BatchConfig(scheduled_delay_ms=200),
    )

    prompts = Prompts(
        pattern=cast(PromptCard, app.service["pattern_prompt"]),
        preference=cast(PromptCard, app.service["preference_prompt"]),
        recommendation=cast(PromptCard, app.service["recommendation_prompt"]),
        search=cast(PromptCard, app.service["search_prompt"]),
    )

    return (app, prompts)


app, prompts = get_app_state()
