# mypy: disable-error-code="attr-defined"

from typing import Callable, Dict, List, Optional

from ..._opsml import (
    EvalRecord,
    EvalRunner,
    EvalScenario,
    EvalScenarios,
    EvaluationConfig,
    ScenarioEvalResults,
)
from ..queue import ScouterQueue
from ..tracing import flush_tracer
from ..tracing import get_tracer as _get_tracer

try:
    from ..._opsml import disable_local_span_capture, enable_local_span_capture
except ImportError:
    enable_local_span_capture = None  # type: ignore[assignment]
    disable_local_span_capture = None  # type: ignore[assignment]

# Baggage key injected into each scenario span so ScouterQueue can tag EvalRecords by scenario.
SCENARIO_TAG_BAGGAGE_KEY = "scouter.eval.scenario_id"

AgentFn = Callable[[str], str]


class EvalOrchestrator:
    """Manages the capture lifecycle, routes scenario types, and delegates to the Rust EvalRunner.

    Works out of the box — pass ``agent_fn`` (a callable that takes a query
    string and returns a response string) and call ``run()``.  Subclass only
    if you need to change *how* scenarios are executed or add lifecycle hooks.

    The orchestrator manages all capture state: queue capture is enabled at
    the start of ``run()`` and disabled in a ``finally`` block, so the queue
    is always returned to its original state.  If a tracer has been
    initialized, local span capture is also toggled automatically.

    Args:
        queue: ScouterQueue instance (source of profiles + capture lifecycle).
        scenarios: Scenario definitions to evaluate.
        agent_fn: Optional callable ``(query) -> response_str``.  When provided,
            the default ``execute_agent`` calls it once for ``initial_query``
            and once per entry in ``predefined_turns``.  When omitted,
            subclass and override ``execute_agent`` instead.

    Examples:
        Minimal usage::

            orch = EvalOrchestrator(
                queue=queue,
                scenarios=scenarios,
                agent_fn=lambda query: my_agent.run(query),
            )
            results = orch.run()

        Subclass for custom execution logic::

            class MyEval(EvalOrchestrator):
                def execute_agent(self, scenario):
                    return self.my_agent.chat(scenario.initial_query)
    """

    def __init__(
        self,
        queue: ScouterQueue,
        scenarios: EvalScenarios,
        agent_fn: Optional[AgentFn] = None,
    ) -> None:
        self._queue = queue
        self._scenarios = scenarios
        self._agent_fn = agent_fn
        self._engine = EvalRunner(
            scenarios=scenarios,
            profiles=queue.genai_profiles(),
        )

    def execute_agent(self, scenario: EvalScenario) -> str:
        """Execute the agent for a scenario.

        The default implementation calls ``agent_fn`` with ``initial_query``,
        then once per entry in ``predefined_turns``, returning the final
        response.  Override to customize execution (e.g. stateful agents,
        custom history management).

        Args:
            scenario: The scenario to execute.

        Returns:
            The agent's final response string.
        """
        if self._agent_fn is None:
            raise NotImplementedError(
                "Either pass agent_fn to EvalOrchestrator() or subclass and override execute_agent()"
            )

        response = self._agent_fn(scenario.initial_query)

        if scenario.is_multi_turn():
            for turn_query in scenario.predefined_turns:
                response = self._agent_fn(turn_query)

        return response

    def on_scenario_start(self, scenario: EvalScenario) -> None:
        """Hook called before a scenario is executed. Override to add custom logic."""

    def on_scenario_complete(self, scenario: EvalScenario, response: str) -> None:
        """Hook called after a scenario is executed. Override to add custom logic."""

    def on_evaluation_complete(self, results: ScenarioEvalResults) -> ScenarioEvalResults:
        """Hook called after evaluation completes. Override to post-process results."""
        return results

    def _setup_capture(self) -> None:
        self._queue.enable_capture()
        try:
            if enable_local_span_capture is not None:
                enable_local_span_capture()
        except Exception:  # noqa: BLE001 pylint: disable=broad-except
            pass

    def _teardown_capture(self) -> None:
        self._queue.disable_capture()
        try:
            if disable_local_span_capture is not None:
                disable_local_span_capture()
        except Exception:  # noqa: BLE001 pylint: disable=broad-except
            pass

    def _execute_with_baggage(self, scenario: EvalScenario) -> str:
        """Run execute_agent inside a span with scenario_id baggage (if tracer available)."""
        try:
            eval_tracer = _get_tracer("scouter.eval")
            span_ctx = eval_tracer.start_as_current_span(
                f"scouter.eval.scenario.{scenario.id}",
                baggage=[{SCENARIO_TAG_BAGGAGE_KEY: scenario.id}],
            )
        except Exception:  # noqa: BLE001 pylint: disable=broad-except
            return self.execute_agent(scenario)
        with span_ctx:
            return self.execute_agent(scenario)

    def _collect_scenario_data(self, scenario: EvalScenario, response: str) -> None:
        records: Dict[str, List[EvalRecord]] = self._queue.drain_all_records()
        self._engine.collect_scenario_data(
            records=records,
            response=response,
            scenario=scenario,
        )

    def run(self, config: Optional[EvaluationConfig] = None) -> ScenarioEvalResults:
        """Execute all scenarios and return evaluation results.

        Manages queue capture and local span capture automatically.
        Each scenario is executed inside a span with ``scouter.eval.scenario_id``
        baggage so that EvalRecords are auto-tagged by the queue bus.

        Args:
            config: Optional evaluation configuration.

        Returns:
            ScenarioEvalResults with metrics across all scenarios.
        """
        self._setup_capture()
        try:
            for scenario in self._scenarios.scenarios:
                if scenario.is_reactive():
                    raise NotImplementedError(
                        "Reactive (simulated user) scenarios not yet supported. "
                        "Use predefined_turns for scripted multi-turn."
                    )

                self.on_scenario_start(scenario)
                response = self._execute_with_baggage(scenario)
                self._collect_scenario_data(scenario, response)
                self.on_scenario_complete(scenario, response)

            try:
                flush_tracer()
            except Exception:  # noqa: BLE001 pylint: disable=broad-except
                pass
            results = self._engine.evaluate(config)
            return self.on_evaluation_complete(results)
        finally:
            self._teardown_capture()
