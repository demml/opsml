from pydantic_settings import BaseSettings
from pathlib import Path
from opsml.app import AppState


class Config(BaseSettings):
    """Configuration for the agent's lifespan events."""

    app_path: Path = Path("service_artifacts")

    class Config:
        env_prefix = "AGENT_LIFESPAN_"


config = Config()


def get_app_state() -> AppState:
    """Helper function to load the AppState for the agent."""
    return AppState.from_path(path=config.app_path)


app = get_app_state()
