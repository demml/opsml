from agent.lifespan import prompts
from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from typing import Optional, cast
from google.genai import types  # For types.Content
from opentelemetry import trace
from opsml.scouter.tracing import ActiveSpan


def before_pattern_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs entry into the pattern recognizer agent and checks 'add_initial_note' in session state.
    If True, returns new Content to *replace* the agent's original instruction.
    If False or not present, returns None, allowing the agent's original instruction to be used.
    """

    tracer = trace.get_tracer("before_pattern_callback")
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    with cast(
        ActiveSpan, tracer.start_as_current_span("before_pattern_callback")
    ) as span:
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("invocation.id", invocation_id)
        span.set_attribute("state", current_state)

    return None


pattern_recognizer = Agent(
    model=prompts.pattern.prompt.model,
    name="PatternRecognizer",
    description="Identifies patterns and themes in user's musical taste.",
    instruction=prompts.pattern.prompt.messages[0].text,
    tools=[],
    output_key="search_strategy",
    before_agent_callback=before_pattern_callback,
)
