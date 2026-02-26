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
    """Example of an after_agent_callback that could be used to log or process the output of the vegan_recipe_agent."""
    agent_name = callback_context.agent_name
    print(f"[Vegan Callback] After model call for agent: {agent_name}")
    print(f"[Vegan Callback] Original LLM response: {llm_response.model_dump_json()}")

    return None  # Return None to keep the original output, or return new Content to replace it


vegan_recipe_agent = Agent(
    model=prompts.vegan.prompt.model,
    name="VeganRecipeAgent",
    description="Generates vegan recipes based on user preferences and dietary restrictions.",
    instruction=prompts.vegan.prompt.messages[0].text,
    after_model_callback=after_model_callback,
)
