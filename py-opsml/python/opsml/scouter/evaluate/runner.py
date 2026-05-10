# mypy: disable-error-code="attr-defined"

import logging
import uuid
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..._opsml import (
    EvalRecord,
    EvalRunner,
    EvalScenario,
    EvalScenarios,
    EvaluationConfig,
    ScenarioEvalResults,
)
from ..queue import ScouterQueue
from ..tracing import (
    disable_local_span_capture,
    enable_local_span_capture,
    flush_tracer,
)
from ..tracing import get_tracer as _get_tracer

logger = logging.getLogger(__name__)

_otel_context: Any = None
_OTEL_AVAILABLE: bool = False

try:  # opentelemetry is an optional runtime dep
    from opentelemetry import context as _otel_context

    _OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover - tracing optional
    pass

# Baggage key injected into each scenario span so ScouterQueue can tag EvalRecords by scenario.
SCENARIO_TAG_BAGGAGE_KEY = "scouter.eval.scenario_id"
RUN_ID_BAGGAGE_KEY = "scouter.eval.run_id"
# Scenario wrapper spans carry infrastructure metadata only; eval records are
# emitted explicitly by span.attach_eval(...) inside agent/callback code.
SCENARIO_WRAPPER_ATTR = {"scouter.eval.wrapper": True}

AgentFn = Callable[[str], Any]
# (initial_query, agent_response, history) -> next user message or termination signal
# history is a list of {"user": str, "agent": Any} dicts for all prior exchanges
SimulatedUserFn = Callable[[str, Any, List[Dict[str, Any]]], str]


def _fresh_otel_context() -> Optional[Any]:
    if not _OTEL_AVAILABLE or _otel_context is None:
        return None
    return _otel_context.Context()


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
        simulated_user_fn: Optional callable ``(initial_query, agent_response) -> next_message``.
            Used for interactive scenarios. Return a string containing
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

        Interactive scenario with simulated user::

            orch = EvalOrchestrator(
                queue=queue,
                scenarios=scenarios,
                agent_fn=lambda q: my_service.chat(q),
                simulated_user_fn=lambda initial_q, response: user_llm.respond(initial_q, response),
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
        self._capture_run_id = uuid.uuid4().hex
        self._engine = EvalRunner(
            scenarios=scenarios,
            profiles=queue.agent_profiles(),
            capture_run_id=self._capture_run_id,
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
        """Execute one agent turn in an interactive loop.

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
        """Generate the next user message in an interactive loop.

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

    def on_scenario_complete(self, scenario: EvalScenario, response: Any, result: Any = None) -> None:
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
        exchanges in the scenario. For non-interactive scenarios it is always
        empty ``[]``. For interactive scenarios it contains every turn up to (but
        not including) the final agent response.

        Default: returns ``response`` unchanged (backward compatible).
        """
        return response

    def _setup_capture(self) -> None:
        self._queue.enable_capture()
        try:
            enable_local_span_capture(self._capture_run_id)
        except Exception:  # noqa: BLE001 pylint: disable=broad-except
            logger.warning(
                "scouter tracer unavailable for eval run %s, spans will not be captured",
                self._capture_run_id,
                exc_info=True,
            )
        if _OTEL_AVAILABLE:
            try:
                from opentelemetry import (
                    trace as _otel_trace,  # pylint: disable=import-outside-toplevel
                )
                from opentelemetry.trace import (  # pylint: disable=import-outside-toplevel
                    NoOpTracerProvider,
                    ProxyTracerProvider,
                )

                provider = _otel_trace.get_tracer_provider()
                if isinstance(provider, (ProxyTracerProvider, NoOpTracerProvider)):
                    logger.warning(
                        "ScouterInstrumentor is not active — third-party spans will not be "
                        "captured for eval run %s. Call ScouterInstrumentor().instrument() "
                        "before EvalOrchestrator.",
                        self._capture_run_id,
                    )
            except Exception:  # noqa: BLE001 pylint: disable=broad-except
                pass

    def _teardown_capture(self) -> None:
        self._queue.disable_capture()
        try:
            disable_local_span_capture(self._capture_run_id)
        except Exception:  # noqa: BLE001 pylint: disable=broad-except
            logger.warning(
                "failed to disable scouter span capture for eval run %s",
                self._capture_run_id,
                exc_info=True,
            )

    @contextmanager
    def _scenario_span(self, scenario: EvalScenario):  # type: ignore[return]
        """Context manager: opens one wrapper span with eval baggage for the full scenario duration."""
        span_ctx = None
        try:
            eval_tracer = _get_tracer("scouter.eval")
            span_ctx = eval_tracer.start_as_current_span(
                f"scouter.eval.scenario.{scenario.id}",
                context=_fresh_otel_context(),
                baggage=[
                    {RUN_ID_BAGGAGE_KEY: self._capture_run_id},
                    {SCENARIO_TAG_BAGGAGE_KEY: scenario.id},
                ],
                attributes=SCENARIO_WRAPPER_ATTR,
            )
        except Exception:  # noqa: BLE001 pylint: disable=broad-except
            logger.warning(
                "scouter tracer unavailable for scenario %s, spans will not be captured",
                scenario.id,
                exc_info=True,
            )
        if span_ctx is not None:
            with span_ctx:
                yield
        else:
            yield

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

    def _execute_interactive(self, scenario: EvalScenario) -> Tuple[Any, List[Dict[str, Any]]]:
        """Run an interactive agent↔simulated-user loop.

        Returns (final_response, history) so the caller owns data collection.
        """
        message = scenario.initial_query
        response: Any = ""
        history: List[Dict[str, Any]] = []

        for _ in range(scenario.max_turns):
            response = self.execute_agent_turn(scenario, message)

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

        return response, history

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
        scenario_results = []
        self._setup_capture()
        try:
            for scenario in self._scenarios.scenarios:
                self.on_scenario_start(scenario)
                with self._scenario_span(scenario):
                    if scenario.is_interactive():
                        response, history = self._execute_interactive(scenario)
                    else:
                        response = self.execute_agent(scenario)
                        history = []
                    scenario_response = self.build_scenario_response(scenario, response, history)
                    self._collect_scenario_data(scenario, scenario_response)
                try:
                    flush_tracer()
                except Exception:  # noqa: BLE001 pylint: disable=broad-except
                    pass
                sr = self._engine.evaluate_scenario(scenario.id)
                scenario_results.append(sr)
                self.on_scenario_complete(scenario, response, sr)
            results = self._engine.finalize(scenario_results, config)
            return self.on_evaluation_complete(results)
        finally:
            self._teardown_capture()
