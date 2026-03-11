from agent.lifespan import prompts
from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from typing import Optional
from google.adk.models.llm_response import LlmResponse
from .models import Recipe
from opentelemetry import trace
from opsml.scouter.tracing import ActiveSpan
from opsml.scouter.evaluate import GenAIEvalRecord
from typing import cast


def parse_model_recipe_output(llm_response: LlmResponse) -> Optional[Recipe]:
    """Example of a function that could be used in an after_model_callback to parse and validate the output of the vegan_recipe_agent against the expected Recipe schema."""

    try:
        # Attempt to parse the LLM response content into the Recipe schema
        recipe = Recipe.model_validate_json(llm_response.content.parts[0].text)  # type: ignore
        return recipe
    except Exception as _e:
        return None


def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """Example of an after_agent_callback that could be used to log or process the output of the vegan_recipe_agent."""

    tracer = trace.get_tracer("vegan_callback")
    with cast(
        ActiveSpan, tracer.start_as_current_span("vegan_recipe_evaluation")
    ) as span:
        recipe = parse_model_recipe_output(llm_response)
        if recipe:
            span.add_queue_item(
                "vegan_eval",
                GenAIEvalRecord(
                    context={"recipe": recipe},
                    session_id=callback_context.session.id,
                ),
            )
        else:
            span.set_status(
                "ERROR",
                "Failed to parse LLM response into Recipe schema",
            )

    return None


vegan_recipe_agent = Agent(
    model=prompts.vegan.prompt.model,
    name="VeganRecipeAgent",
    description="Generates vegan recipes based on user preferences and dietary restrictions.",
    instruction=prompts.vegan.prompt.messages[0].text,
    after_model_callback=after_model_callback,
    output_schema=Recipe,
)
