from opsml.scouter.tracing import (
    ScouterInstrumentor,
    TracerProvider,
    BatchConfig,
    ActiveSpan,
)
from opsml.scouter.transport import GrpcConfig
from opsml.scouter.queue import ScouterQueue, GenAIEvalRecord
from google.adk.agents.llm_agent import Agent
from .setup.prompt import (
    recipe_card,
    recipe_response_card,
    recipe_generation_eval_profile,
    recipe_response_eval_profile,
)
from .setup.models import Recipe
from google.adk.agents.callback_context import CallbackContext
from google.genai import types  # For types.Content
from typing import Optional
from opentelemetry import trace
from typing import cast
from google.adk.agents.sequential_agent import SequentialAgent


queue = ScouterQueue.from_profile(
    profile=[recipe_generation_eval_profile, recipe_response_eval_profile],
    transport_config=GrpcConfig(),
)

provider = TracerProvider(
    transport_config=GrpcConfig(),
    batch_config=BatchConfig(scheduled_delay_ms=200),
    scouter_queue=queue,
)
ScouterInstrumentor().instrument(tracer_provider=provider)


def recipe_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs exit from an agent and checks 'add_concluding_note' in session state.
    If True, returns new Content to *replace* the agent's original output.
    If False or not present, returns None, allowing the agent's original output to be used.
    """

    tracer = trace.get_tracer("after_agent_callback")
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    with cast(ActiveSpan, tracer.start_as_current_span("recipe_callback")) as span:
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("invocation.id", invocation_id)
        span.set_attribute("state", str(current_state))

        queue_record = GenAIEvalRecord(
            context={
                "recipe": current_state.get("recipe", {}),
            },
        )

        span.add_queue_item("recipe_generation", queue_record)

    return None  # Return None to use the agent's original output


def recipe_response_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs exit from an agent and checks 'add_concluding_note' in session state.
    If True, returns new Content to *replace* the agent's original output.
    If False or not present, returns None, allowing the agent's original output to be used.
    """

    tracer = trace.get_tracer("after_agent_callback")
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    with cast(ActiveSpan, tracer.start_as_current_span("recipe_callback")) as span:
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("invocation.id", invocation_id)
        span.set_attribute("state", str(current_state))

        queue_record = GenAIEvalRecord(
            context={
                "recipe_response": current_state.get("recipe_response", {}),
            },
        )

        span.add_queue_item("recipe_response", queue_record)

    return None  # Return None to use the agent's original output


recipe_agent = Agent(
    model=recipe_card.prompt.model,
    name="RecipeAgent",
    description="An agent that provides vegetarian recipes based on user requests.",
    instruction=recipe_card.prompt.message.text,
    output_key="recipe",
    output_schema=Recipe,
    after_agent_callback=recipe_agent_callback,
)


response_agent = Agent(
    name="RecipeResponseAgent",
    model=recipe_response_card.prompt.model,
    description="An agent that provides detailed recipes based on user requests.",
    instruction=recipe_response_card.prompt.message.text,
    output_key="recipe_response",
    after_agent_callback=recipe_response_agent_callback,
)


code_pipeline_agent = SequentialAgent(
    name="RecipePipelineAgent",
    sub_agents=[recipe_agent, response_agent],
    description="Executes a sequence of recipe generation and response.",
)

root_agent = code_pipeline_agent
