from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Union, cast

from opsml import PromptCard
from opsml.app import AppState
from opsml.scouter.evaluate import EvalScenarios
from opsml.scouter.tracing import BatchConfig
from opsml.scouter.transport import GrpcConfig, MockConfig

_BASE_DIR = Path(__file__).resolve().parent
_SPEC_DIR = _BASE_DIR.parent
TransportConfig = Union[GrpcConfig, MockConfig]


@dataclass(frozen=True)
class SharedConfig:
    app: AppState
    prompt: PromptCard
    scenarios: EvalScenarios


def _transport_config() -> TransportConfig:
    if os.getenv("APP_ENV") in {"staging", "production"}:
        return GrpcConfig()
    return MockConfig()


@lru_cache(maxsize=1)
def get_shared_config() -> SharedConfig:
    scenarios = EvalScenarios.from_path(_BASE_DIR / "scenarios.jsonl")

    app = AppState.from_spec(
        path=_SPEC_DIR / "opsmlspec.yaml",
        transport_config=_transport_config(),
        register=True,
    )
    app.instrument(batch_config=BatchConfig(scheduled_delay_ms=200))

    return SharedConfig(
        app=app,
        prompt=cast(PromptCard, app.service["support_prompt"]),
        scenarios=scenarios,
    )


def teardown() -> None:
    try:
        config = get_shared_config()
    except Exception:
        return
    config.app.shutdown()
    get_shared_config.cache_clear()
