from pathlib import Path

import pydantic
import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    """Configuration for your agent service. Set via environment variables."""

    app_path: Path = Path(__file__).parent / "opsmlspec.yaml"
    agent_url: pydantic.AnyHttpUrl = pydantic.Field(
        default=pydantic.AnyHttpUrl("http://localhost:8002"),
        description="Base URL your agent is served on",
    )


config = Config()
