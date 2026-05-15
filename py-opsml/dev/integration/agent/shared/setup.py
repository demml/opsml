from __future__ import annotations

import os
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Union, cast

from pydantic import BaseModel, ConfigDict
from opsml import PromptCard
from opsml.app import AppState
from opsml.scouter.drift import AgentEvalProfile
from opsml.scouter.tracing import BatchConfig
from opsml.scouter.transport import GrpcConfig, MockConfig

os.environ.setdefault("OPSML_TRACKING_URI", "http://localhost:8090")
os.environ.setdefault("SCOUTER_SERVER_URI", "http://localhost:8000")
os.environ.setdefault("SCOUTER_GRPC_URI", "http://localhost:50051")

_BASE_DIR = Path(__file__).resolve().parent.parent
TransportConfig = Union[GrpcConfig, MockConfig]

_config: AgentConfig | None = None
_config_key: tuple[str, str, bool] | None = None

APP_NAME = "opsml_e2e_agent"


class Prompts(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    triage: PromptCard
    responder: PromptCard


@dataclass(frozen=True)
class PromptSpec:
    alias: str
    card: PromptCard
    eval_profile: AgentEvalProfile
    task_ids: set[str]


@dataclass(frozen=True)
class AttachedEval:
    run_id: str
    agent_name: str
    profile_uid: str
    record_id: str
    session_id: str
    trace_id: str
    span_id: str


@dataclass
class AgentConfig:
    app: AppState
    prompts: Prompts
    triage: PromptSpec
    responder: PromptSpec
    attached_evals: list[AttachedEval] = field(default_factory=list)
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    _attached_eval_ids: set[str] = field(default_factory=set, init=False, repr=False)
    _attached_eval_lock: Any = field(
        default_factory=threading.RLock, init=False, repr=False
    )

    def begin_run(self, run_id: str | None = None) -> str:
        """Reset the integration-test eval ledger for a new harness run."""
        with self._attached_eval_lock:
            self.run_id = run_id or uuid.uuid4().hex
            self.attached_evals.clear()
            self._attached_eval_ids.clear()
            return self.run_id

    def clear_attached_evals(self) -> None:
        """Clear attached evals without changing the current run identity."""
        with self._attached_eval_lock:
            self.attached_evals.clear()
            self._attached_eval_ids.clear()

    def record_attached_eval(self, attached_eval: AttachedEval) -> None:
        """Record eval metadata for end-of-run integration assertions."""
        with self._attached_eval_lock:
            if attached_eval.record_id in self._attached_eval_ids:
                return
            self._attached_eval_ids.add(attached_eval.record_id)
            self.attached_evals.append(attached_eval)

    def attached_eval_snapshot(self) -> list[AttachedEval]:
        """Return a stable snapshot for assertions that need thread-safe reads."""
        with self._attached_eval_lock:
            return list(self.attached_evals)


def get_shared_config(
    *,
    transport_config: TransportConfig | None = None,
    register: bool = True,
) -> AgentConfig:
    global _config, _config_key
    config_key = _cache_key(transport_config, register)
    if _config is not None and _config_key == config_key:
        return _config
    if _config is not None:
        _config.app.shutdown()
        _config = None
        _config_key = None

    app = AppState.from_spec(
        path=_BASE_DIR / "opsmlspec.yaml",
        transport_config=cast(Any, transport_config or GrpcConfig()),
        register=register,
    )
    app.instrument(batch_config=BatchConfig(scheduled_delay_ms=200))

    triage_card = cast(PromptCard, app.service["triage_prompt"])
    responder_card = cast(PromptCard, app.service["responder_prompt"])
    prompts = Prompts(triage=triage_card, responder=responder_card)
    _config = AgentConfig(
        app=app,
        prompts=prompts,
        triage=_prompt_spec("triage_evaluation", triage_card),
        responder=_prompt_spec("responder_evaluation", responder_card),
    )
    _config_key = config_key
    return _config


def _cache_key(
    transport_config: TransportConfig | None,
    register: bool,
) -> tuple[str, str, bool]:
    transport_type = GrpcConfig if transport_config is None else type(transport_config)
    transport_value = "default" if transport_config is None else repr(transport_config)
    return (
        f"{transport_type.__module__}.{transport_type.__qualname__}",
        transport_value,
        register,
    )


def _prompt_spec(alias: str, card: PromptCard) -> PromptSpec:
    profile = card.eval_profile
    if profile is None:
        raise RuntimeError(f"Prompt card '{alias}' did not load an eval profile")
    tasks = [
        *profile.assertion_tasks,
        *profile.llm_judge_tasks,
        *profile.trace_assertion_tasks,
    ]
    return PromptSpec(
        alias=alias,
        card=card,
        eval_profile=profile,
        task_ids={str(task.id) for task in tasks},
    )


def teardown() -> None:
    global _config, _config_key
    if _config is None:
        return
    _config.app.shutdown()
    _config = None
    _config_key = None
