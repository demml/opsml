from agent.lifespan import prompts
from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types  # For types.Content
from typing import Optional
from opentelemetry import trace
from typing import cast
from opsml.scouter.evaluate import GenAIEvalRecord
from opsml.scouter.tracing import ActiveSpan


def before_recommendation_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs entry into the recommendation generator agent and checks 'add_initial_note' in session state.
    If True, returns new Content to *replace* the agent's original instruction.
    If False or not present, returns None, allowing the agent's original instruction to be used.
    """

    tracer = trace.get_tracer("before_recommendation_callback")
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    with cast(ActiveSpan, tracer.start_as_current_span("pre_recommendation_callback")) as span:
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("invocation.id", invocation_id)
        span.set_attribute("state", current_state)

    return None


def after_recommendation_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs exit from an agent and checks 'add_concluding_note' in session state.
    If True, returns new Content to *replace* the agent's original output.
    If False or not present, returns None, allowing the agent's original output to be used.
    """

    tracer = trace.get_tracer("after_recommendation_callback")
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    with cast(ActiveSpan, tracer.start_as_current_span("recommendation_callback")) as span:
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("invocation.id", invocation_id)

        queue_record = GenAIEvalRecord(
            context={
                "final_recommendations": current_state.get("final_recommendations", {}),
            },
        )

        span.add_queue_item("recommendation", queue_record)

    return None


recommendation_generator = Agent(
    model=prompts.recommendation.prompt.model,
    name="RecommendationGenerator",
    description="Generates final personalized recommendations with reasoning.",
    instruction=prompts.recommendation.prompt.messages[0].text,
    tools=[],
    output_key="final_recommendations",  # Reads candidates, produces final output
    after_agent_callback=after_recommendation_callback,  # Logs after execution and can modify output
    before_agent_callback=before_recommendation_callback,  # Logs before execution and can modify instruction
)
