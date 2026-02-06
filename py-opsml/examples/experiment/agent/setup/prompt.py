from opsml.card import PromptCard, RegistryType
from opsml.genai import Prompt
from opsml.scouter.drift import GenAIEvalProfile
from .models import Recipe
from .tasks import recipe_tasks, recipe_response_tasks
from opsml.card import CardRegistry


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
            "Output Format:\n"
            "Respond with a JSON object that adheres to the following structure:\n"
            "```json\n"
            "{\n"
            '  "name": "Recipe Name",\n'
            '  "ingredients": [\n'
            '    {"name": "Ingredient Name", "quantity": "Amount", "unit": "Unit"},\n'
            "    ...\n"
            "  ],\n"
            '  "directions": [\n'
            '    "Step 1",\n'
            '    "Step 2",\n'
            "    ...\n"
            "  ],\n"
            '  "prep_time_minutes": Number,\n'
            '  "servings": Number\n'
            "}\n"
            "```\n"
            "Make sure to follow the output format exactly, as it will be parsed programmatically."
        ),
        model="gemini-2.5-flash-lite",
        provider="gemini",
        output_type=Recipe,
    )


def create_recipe_response_prompt() -> Prompt:
    """
    Builds a prompt for generating a vegetarian recipe with structured output.
    """
    return Prompt(
        messages=(
            "You are an expert chef specializing in vegetarian cuisine. Your task is to create "
            "take a recipe from a previous step and give the user a full detailed recipe based on the user's request.\n\n"
        ),
        model="gemini-2.5-flash-lite",
        provider="gemini",
        output_type=Recipe,
    )


def create_recipe_prompt_card() -> tuple[PromptCard, PromptCard, GenAIEvalProfile, GenAIEvalProfile]:
    """
    Creates a response prompt card for generating recipes.

    Returns:
        PromptCard: A prompt card for generating recipes.
    """

    recipe_generation_eval_profile = GenAIEvalProfile(
        tasks=recipe_tasks,
        alias="recipe_generation",
    )
    recipe_card = PromptCard(
        prompt=create_recipe_generation_prompt(),
        space="opsml",
        name="recipe_generation",
        eval_profile=recipe_generation_eval_profile,
    )

    recipe_response_eval_profile = GenAIEvalProfile(
        tasks=recipe_response_tasks,
        alias="recipe_response",
    )
    recipe_response_card = PromptCard(
        prompt=create_recipe_response_prompt(),
        space="opsml",
        name="recipe_detail_generation",
        eval_profile=recipe_response_eval_profile,
    )

    reg: CardRegistry[PromptCard] = CardRegistry(registry_type=RegistryType.Prompt)
    reg.register_card(recipe_card)
    reg.register_card(recipe_response_card)

    return (
        recipe_card,
        recipe_response_card,
        recipe_generation_eval_profile,
        recipe_response_eval_profile,
    )


(
    recipe_card,
    recipe_response_card,
    recipe_generation_eval_profile,
    recipe_response_eval_profile,
) = create_recipe_prompt_card()
