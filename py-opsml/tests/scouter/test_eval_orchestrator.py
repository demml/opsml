from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from opsml.scouter.evaluate.runner import EvalOrchestrator
import opsml.scouter.evaluate.runner as runner_module


@dataclass
class FakeScenario:
    id: str
    initial_query: str
    predefined_turns: list[str]
    termination_signal: str | None = None
    max_turns: int = 3
    interactive: bool = False

    def is_multi_turn(self) -> bool:
        return len(self.predefined_turns) > 0

    def is_interactive(self) -> bool:
        return self.interactive


@dataclass
class FakeScenarios:
    scenarios: list[FakeScenario]


class FakeQueue:
    def __init__(self) -> None:
        self.capture_enabled = False
        self.enable_calls = 0
        self.disable_calls = 0
        self.drain_calls = 0

    def agent_profiles(self) -> list[Any]:
        return []

    def enable_capture(self) -> None:
        self.capture_enabled = True
        self.enable_calls += 1

    def disable_capture(self) -> None:
        self.capture_enabled = False
        self.disable_calls += 1

    def drain_all_records(self) -> dict[str, list[Any]]:
        self.drain_calls += 1
        return {"records": []}


class FakeEvalRunner:
    def __init__(self, scenarios: FakeScenarios, profiles: list[Any]) -> None:
        self.scenarios = scenarios
        self.profiles = profiles
        self.collect_calls: list[dict[str, Any]] = []
        self.evaluate_calls = 0

    def collect_scenario_data(self, records: dict[str, list[Any]], response: Any, scenario: FakeScenario) -> None:
        self.collect_calls.append(
            {"records": records, "response": response, "scenario_id": scenario.id}
        )

    def evaluate(self, _config: Any) -> dict[str, Any]:
        self.evaluate_calls += 1
        return {"ok": True, "count": len(self.collect_calls)}


def test_eval_orchestrator_non_interactive_capture_lifecycle(monkeypatch):
    monkeypatch.setattr(runner_module, "EvalRunner", FakeEvalRunner)
    monkeypatch.setattr(runner_module, "enable_local_span_capture", lambda: None)
    monkeypatch.setattr(runner_module, "disable_local_span_capture", lambda: None)
    monkeypatch.setattr(runner_module, "flush_tracer", lambda: None)
    monkeypatch.setattr(runner_module, "_get_tracer", lambda _: (_ for _ in ()).throw(RuntimeError("no tracer")))

    queue = FakeQueue()
    scenarios = FakeScenarios(
        scenarios=[
            FakeScenario(
                id="scenario-1",
                initial_query="hello",
                predefined_turns=["next"],
                interactive=False,
            )
        ]
    )

    calls: list[str] = []
    orchestrator = EvalOrchestrator(
        queue=queue,
        scenarios=scenarios,  # type: ignore[arg-type]
        agent_fn=lambda message: calls.append(message) or f"response:{message}",
    )

    result = orchestrator.run()

    assert result["ok"] is True
    assert queue.enable_calls == 1
    assert queue.disable_calls == 1
    assert queue.capture_enabled is False
    assert queue.drain_calls == 1
    assert calls == ["hello", "next"]
    assert orchestrator._engine.collect_calls[0]["scenario_id"] == "scenario-1"  # pylint: disable=protected-access


def test_eval_orchestrator_interactive_turns_and_history(monkeypatch):
    monkeypatch.setattr(runner_module, "EvalRunner", FakeEvalRunner)
    monkeypatch.setattr(runner_module, "enable_local_span_capture", lambda: None)
    monkeypatch.setattr(runner_module, "disable_local_span_capture", lambda: None)
    monkeypatch.setattr(runner_module, "flush_tracer", lambda: None)
    monkeypatch.setattr(runner_module, "_get_tracer", lambda _: (_ for _ in ()).throw(RuntimeError("no tracer")))

    queue = FakeQueue()
    scenarios = FakeScenarios(
        scenarios=[
            FakeScenario(
                id="interactive-1",
                initial_query="start",
                predefined_turns=[],
                termination_signal="done",
                max_turns=4,
                interactive=True,
            )
        ]
    )

    agent_messages: list[str] = []
    simulated_history_sizes: list[int] = []

    def agent_fn(message: str) -> str:
        agent_messages.append(message)
        return f"agent:{message}"

    def simulated_user_fn(_initial: str, _response: Any, history: list[dict[str, Any]]) -> str:
        simulated_history_sizes.append(len(history))
        return "done" if len(history) >= 1 else "continue"

    orchestrator = EvalOrchestrator(
        queue=queue,
        scenarios=scenarios,  # type: ignore[arg-type]
        agent_fn=agent_fn,
        simulated_user_fn=simulated_user_fn,
    )

    result = orchestrator.run()

    assert result["ok"] is True
    assert queue.drain_calls == 1
    assert agent_messages == ["start", "continue"]
    assert simulated_history_sizes == [0, 1]
