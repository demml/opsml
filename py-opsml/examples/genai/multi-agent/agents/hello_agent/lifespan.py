import contextlib
import functools
from collections.abc import AsyncIterator
from typing import cast

from pydantic import BaseModel, ConfigDict
from opsml import PromptCard
from opsml.app import AppState
from opsml.card import AgentSpec
from opsml.scouter.tracing import BatchConfig
from opsml.scouter.transport import GrpcConfig
from starlette.applications import Starlette

from .config import config


class Prompts(BaseModel):
    """Container for PromptCards loaded from the OpsML registry."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    hello: PromptCard


# @functools.cache makes initialization lazy (called on first use, not at import time)
# and ensures a single shared instance across the process — safe to mock in tests.
@functools.cache
def get_app_state() -> tuple[AppState, Prompts, AgentSpec]:
    """Load and register the agent service from opsmlspec.yaml."""
    app = AppState.from_spec(path=config.app_path)
    agent_spec = app.service.agent_card()
    app.instrument(transport_config=GrpcConfig(), batch_config=BatchConfig(scheduled_delay_ms=200))
    return app, Prompts(hello=cast(PromptCard, app.service["hello_agent"])), agent_spec


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    yield
