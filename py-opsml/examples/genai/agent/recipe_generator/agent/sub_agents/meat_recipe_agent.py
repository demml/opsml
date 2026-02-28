from agent.lifespan import prompts
from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from typing import Optional, cast
from google.adk.models import LlmResponse
from .models import Recipe
from opentelemetry import trace
from opsml.scouter.tracing import ActiveSpan
from opsml.card import PromptCard


def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """Example of an after_agent_callback that could be used to log or process the output of the vegan_recipe_agent."""

    tracer = trace.get_tracer("meat_recipe")

    with cast(ActiveSpan, tracer.start_as_current_span("meat_id")) as span:
        meat_card = cast(PromptCard, prompts.meat)
        if meat_card.eval_profile:
            span.set_entity(meat_card.eval_profile.uid)
        return None


meat_recipe_agent = Agent(
    model=prompts.meat.prompt.model,
    name="MeatRecipeAgent",
    description="Generates meat-based recipes based on user preferences and dietary restrictions.",
    instruction=prompts.meat.prompt.messages[0].text,
    after_model_callback=after_model_callback,
    output_schema=Recipe,
)
