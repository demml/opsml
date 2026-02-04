from opsml.card import PromptCard
from opsml.genai import Prompt
from opsml.scouter.drift import GenAIAlertConfig, GenAIEvalConfig
from opsml.scouter import CommonCrons
from app.models import Recipe  # type: ignore
from .evaluation.tasks import tasks


def create_recipe_generation_prompt() -> Prompt:
    """
    Builds a prompt for generating a vegetarian recipe with structured output.
    """
    return Prompt(
        messages=(
            "You are an expert chef specializing in vegetarian cuisine. Your task is to create "
            "a complete vegetarian recipe based on the user's request.\n\n"
            "Guidelines:\n"
            "- Ensure all ingredients are vegetarian (no meat, poultry, or seafood)\n"
            "- Recipe should be easy to follow and practical for home cooks\n"
            "- Provide specific quantities and units for each ingredient\n"
            "- Include detailed, step-by-step cooking directions\n"
            "- Specify prep time (less than 120 minutes) and number of servings\n"
            "- Make the recipe practical and easy to follow\n\n"
            "User Request:\n"
            "${user_request}\n\n"
            "Generate a complete recipe:"
        ),
        model="gemini-2.5-flash-lite",
        provider="gemini",
        output_type=Recipe,
    )


def create_recipe_prompt_card() -> PromptCard:
    """
    Creates a response prompt card for generating recipes.

    Returns:
        PromptCard: A prompt card for generating recipes.
    """
    recipe_card = PromptCard(
        prompt=create_recipe_generation_prompt(),
        space="opsml",
        name="recipe_generation",
    )

    recipe_card.create_eval_profile(
        alias="recipe_metrics",
        config=GenAIEvalConfig(
            sample_ratio=1.0,
            alert_config=GenAIAlertConfig(schedule=CommonCrons.Every6Hours),
        ),
        tasks=tasks,
    )

    return recipe_card
