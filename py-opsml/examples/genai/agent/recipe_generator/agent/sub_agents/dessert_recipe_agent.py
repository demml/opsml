from agent.lifespan import prompts
from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from typing import Optional
from google.adk.models import LlmResponse
from .models import Recipe


def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """Example of an after_agent_callback that could be used to log or process the output of the dessert_recipe_agent."""
    response = llm_response.content.parts[0].text

    # load the response into the Recipe pydantic model to validate the output
    try:
        recipe = Recipe.model_validate_json(response)
    except Exception as e:
        print(f"[Dessert Callback] Error parsing recipe: {e}")
        print(f"[Dessert Callback] Parsed recipe: {recipe}")

    return None  # Return None to keep the original output, or return new Content to replace it


dessert_recipe_agent = Agent(
    model=prompts.dessert.prompt.model,
    name="DessertRecipeAgent",
    description="Generates dessert recipes based on user preferences and dietary restrictions.",
    instruction=prompts.dessert.prompt.messages[0].text,
    after_model_callback=after_model_callback,
    output_schema=Recipe,
)
