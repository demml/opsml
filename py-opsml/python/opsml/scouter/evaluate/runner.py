# mypy: disable-error-code="attr-defined"

from typing import Any, Callable, Dict, List, Optional

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

AgentFn = Callable[[str], Any]
# (initial_query, agent_response, history) -> next user message or termination signal
# history is a list of {"user": str, "agent": Any} dicts for all prior exchanges
SimulatedUserFn = Callable[[str, Any, List[Dict[str, Any]]], str]


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
        simulated_user_fn: Optional callable ``(initial_query, agent_response, history) -> next_message``.
            Used for reactive scenarios. Return a string containing
            ``scenario.termination_signal`` to end the loop. When omitted,
            subclass and override ``execute_simulated_user_turn`` instead.

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

        Reactive scenario with simulated user::

            orch = EvalOrchestrator(
                queue=queue,
                scenarios=scenarios,
                agent_fn=lambda q: my_service.chat(q),
                simulated_user_fn=lambda initial_q, response, history: user_llm.respond(initial_q, response),
            )
            results = orch.run()
    """

    def __init__(
        self,
        queue: ScouterQueue,
        scenarios: EvalScenarios,
        agent_fn: Optional[AgentFn] = None,
        simulated_user_fn: Optional[SimulatedUserFn] = None,
    ) -> None:
        self._queue = queue
        self._scenarios = scenarios
        self._agent_fn = agent_fn
        self._simulated_user_fn = simulated_user_fn
        self._engine = EvalRunner(
            scenarios=scenarios,
            profiles=queue.agent_profiles(),
        )

    def execute_agent(self, scenario: EvalScenario) -> Any:
        """Execute the agent for a scenario.

        The default implementation calls ``agent_fn`` with ``initial_query``,
        then once per entry in ``predefined_turns``, returning the final
        response.  Override to customize execution (e.g. stateful agents,
        custom history management, or returning structured output).

        Args:
            scenario: The scenario to execute.

        Returns:
            The agent's final response. Can be any JSON-serializable value.
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

    def execute_agent_turn(self, scenario: EvalScenario, message: str) -> Any:
        """Execute one agent turn in a reactive loop.

        Default: calls ``agent_fn(message)``. Override for frameworks that
        need the full scenario context or manage their own session state.

        Args:
            scenario: The scenario being executed.
            message: The current user message to send to the agent.

        Returns:
            The agent's response. Can be any JSON-serializable value.
        """
        if self._agent_fn is None:
            raise NotImplementedError(
                "Either pass agent_fn to EvalOrchestrator() or subclass and override execute_agent_turn()"
            )
        return self._agent_fn(message)

    def execute_simulated_user_turn(
        self,
        scenario: EvalScenario,
        initial_query: str,
        agent_response: Any,
        history: List[Dict[str, Any]],
    ) -> str:
        """Generate the next user message in a reactive loop.

        Given the original intent, the agent's latest response, and all prior
        exchanges, decide whether to ask a follow-up or signal completion by
        returning a string that contains ``scenario.termination_signal``.

        ``history`` is a list of ``{"user": str, "agent": Any}`` dicts for all
        exchanges that preceded the current ``agent_response``. Use it when
        satisfaction depends on the cumulative conversation rather than any
        single reply.

        Args:
            scenario: The scenario being executed.
            initial_query: The original query that started the conversation.
            agent_response: The agent's most recent response (any type).
            history: All prior ``(user_message, agent_response)`` exchanges.

        Returns:
            Next user message, or a string containing ``termination_signal`` to end the loop.
        """
        if self._simulated_user_fn is None:
            raise NotImplementedError(
                "Either pass simulated_user_fn to EvalOrchestrator() or subclass and override execute_simulated_user_turn()"
            )
        return self._simulated_user_fn(initial_query, agent_response, history)

    def on_scenario_start(self, scenario: EvalScenario) -> None:
        """Hook called before a scenario is executed. Override to add custom logic."""

    def on_scenario_complete(self, scenario: EvalScenario, response: Any) -> None:
        """Hook called after a scenario is executed. Override to add custom logic."""

    def on_evaluation_complete(self, results: ScenarioEvalResults) -> ScenarioEvalResults:
        """Hook called after evaluation completes. Override to post-process results."""
        return results

    def build_scenario_response(
        self,
        scenario: EvalScenario,
        response: Any,
        history: List[Dict[str, Any]],
    ) -> Any:
        """Transform the agent output before scenario-level task evaluation.

        Override to return a dict, list, number, Pydantic model, or the full
        conversation history. The return value is what scenario task
        ``context_path`` expressions navigate against via ``"response.<field>"``.

        ``history`` is a list of ``{"user": str, "agent": Any}`` dicts for all
        exchanges in the scenario. For non-reactive scenarios it is always
        empty ``[]``. For reactive scenarios it contains every turn up to (but
        not including) the final agent response.

        Default: returns ``response`` unchanged (backward compatible).
        """
        return response

    def _setup_capture(self) -> None:
        self._queue.enable_capture()
        try:
            enable_local_span_capture()
        except Exception:  # noqa: BLE001 pylint: disable=broad-except
            pass

    def _teardown_capture(self) -> None:
        self._queue.disable_capture()
        try:
            disable_local_span_capture()
        except Exception:  # noqa: BLE001 pylint: disable=broad-except
            pass

    def _execute_with_baggage(self, scenario: EvalScenario) -> Any:
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

    def _run_agent_turn(self, scenario: EvalScenario, message: str) -> Any:
        """Run execute_agent_turn inside a scenario span if a tracer is available."""
        try:
            eval_tracer = _get_tracer("scouter.eval")
            span_ctx = eval_tracer.start_as_current_span(
                f"scouter.eval.scenario.{scenario.id}",
                baggage=[{SCENARIO_TAG_BAGGAGE_KEY: scenario.id}],
            )
        except Exception:  # noqa: BLE001 pylint: disable=broad-except
            return self.execute_agent_turn(scenario, message)
        with span_ctx:
            return self.execute_agent_turn(scenario, message)

    def _check_termination(self, scenario: EvalScenario, user_message: str) -> bool:
        if scenario.termination_signal is None:
            return False
        return scenario.termination_signal in user_message

    def _collect_scenario_data(self, scenario: EvalScenario, response: Any) -> None:
        records: Dict[str, List[EvalRecord]] = self._queue.drain_all_records()
        self._engine.collect_scenario_data(
            records=records,
            response=response,
            scenario=scenario,
        )

    def _execute_reactive(self, scenario: EvalScenario) -> Any:
        """Run a reactive agent↔simulated-user loop.

        The agent is a black box: it receives a message and returns a response,
        managing its own session state internally. The simulated user drives
        continuation based on the original intent, the latest response, and the
        full prior exchange history — enabling cumulative satisfaction decisions.
        All records emitted across all turns are drained once at the end.
        """
        message = scenario.initial_query
        response: Any = ""
        history: List[Dict[str, Any]] = []

        for _ in range(scenario.max_turns):
            response = self._run_agent_turn(scenario, message)

            next_message = self.execute_simulated_user_turn(
                scenario,
                initial_query=scenario.initial_query,
                agent_response=response,
                history=history,
            )

            history.append({"user": message, "agent": response})

            if self._check_termination(scenario, next_message):
                break

            message = next_message

        scenario_response = self.build_scenario_response(scenario, response, history)
        self._collect_scenario_data(scenario, scenario_response)
        return response

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
                self.on_scenario_start(scenario)

                if scenario.is_reactive():
                    response = self._execute_reactive(scenario)
                else:
                    response = self._execute_with_baggage(scenario)
                    scenario_response = self.build_scenario_response(scenario, response, [])
                    self._collect_scenario_data(scenario, scenario_response)

                self.on_scenario_complete(scenario, response)

            try:
                flush_tracer()
            except Exception:  # noqa: BLE001 pylint: disable=broad-except
                pass
            results = self._engine.evaluate(config)
            return self.on_evaluation_complete(results)
        finally:
            self._teardown_capture()
