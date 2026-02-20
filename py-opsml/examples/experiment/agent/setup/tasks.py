from opsml.genai import Prompt
from opsml.scouter.evaluate import (
    LLMJudgeTask,
    ComparisonOperator,
    AssertionTask,
    TraceAssertionTask,
    TraceAssertion,
    SpanFilter,
)
from pydantic import BaseModel
from typing import List


class VegetarianValidation(BaseModel):
    is_vegetarian: bool
    reason: str
    non_vegetarian_ingredients: List[str]


class HelpfulSuggestion(BaseModel):
    is_practical: bool
    reason: str


def validate_recipe_correctness_response() -> Prompt:
    """
    Builds a prompt for validating that a recipe is practical and easy to follow.
    """
    return Prompt(
        messages=(
            "You are a culinary expert tasked with evaluating the practicality of a given recipe. "
            "Your goal is to determine whether the recipe is practical and easy to follow for home cooks.\n\n"
            "A practical recipe should:\n"
            "- Use common, easily accessible ingredients\n"
            "- Have clear, step-by-step instructions\n"
            "- Be feasible to prepare within a reasonable time frame (e.g., under 120 minutes)\n"
            "- Not require advanced cooking techniques or equipment\n\n"
            "Analyze the following recipe and provide your evaluation.\n\n"
            "Recipe:\n"
            "${recipe}\n\n"
            "Evaluation:\n"
            "Provide your evaluation as a JSON object with:\n"
            "- is_practical: boolean indicating if the recipe is practical\n"
            "- reason: explanation for your determination\n"
        ),
        model="gemini-2.5-flash-lite",
        provider="gemini",
        output_type=HelpfulSuggestion,
    )


def create_vegetarian_validation_prompt() -> Prompt:
    """
    Builds a prompt for validating that a recipe is truly vegetarian.
    """
    return Prompt(
        messages=(
            "You are a nutrition expert specializing in dietary restrictions. Your task is to verify "
            "whether a recipe is truly vegetarian.\n\n"
            "A vegetarian recipe:\n"
            "- Contains NO meat (beef, pork, lamb, etc.)\n"
            "- Contains NO poultry (chicken, turkey, duck, etc.)\n"
            "- Contains NO seafood (fish, shrimp, shellfish, etc.)\n"
            "- MAY contain eggs, dairy, and honey\n"
            "- MAY contain plant-based meat alternatives\n\n"
            "Analyze the following recipe and determine if it meets vegetarian standards.\n\n"
            "Recipe:\n"
            "${recipe_response}\n\n"
            "Provide your evaluation as a JSON object with:\n"
            "- is_vegetarian: boolean indicating if the recipe is vegetarian\n"
            "- reason: explanation for your determination\n"
            "- non_vegetarian_ingredients: list of any non-vegetarian ingredients found (empty list if none)\n\n"
            "Evaluation:"
        ),
        model="gemini-2.5-flash-lite",
        provider="gemini",
        output_type=VegetarianValidation,
    )


llm_judge_task = LLMJudgeTask(  # LLM judges validate the prompt outputs, not original context
    id="vegetarian_validation",
    prompt=create_vegetarian_validation_prompt(),
    expected_value=True,
    operator=ComparisonOperator.Equals,
    field_path="is_vegetarian",
    description="Validate that the recipe is truly vegetarian",
)

recipe_correctness_task = LLMJudgeTask(  # LLM judges validate the prompt outputs, not original context
    id="recipe_correctness_validation",
    prompt=validate_recipe_correctness_response(),
    expected_value=True,
    operator=ComparisonOperator.Equals,
    field_path="is_practical",
    description="Validate that the recipe is practical and easy to follow",
)


has_directions = AssertionTask(
    id="has_directions",
    field_path="recipe.directions",
    operator=ComparisonOperator.HasLengthGreaterThan,
    expected_value=0,
    description="Verify the recipe contains cooking directions",
)

trace_task = TraceAssertionTask(
    id="check_span_or_filter",
    assertion=TraceAssertion.span_count(filter=SpanFilter.by_name("recipe_callback")),
    operator=ComparisonOperator.GreaterThanOrEqual,
    expected_value=2,
)


recipe_tasks: list[LLMJudgeTask | AssertionTask | TraceAssertionTask] = [
    llm_judge_task,
    has_directions,
    trace_task,
]

recipe_response_tasks: list[LLMJudgeTask | AssertionTask | TraceAssertionTask] = [
    recipe_correctness_task,
]
