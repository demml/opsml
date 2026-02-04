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
            "${recipe}\n\n"
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


llm_judge_task = (
    LLMJudgeTask(  # LLM judges validate the prompt outputs, not original context
        id="vegetarian_validation",
        prompt=create_vegetarian_validation_prompt(),
        expected_value=True,
        operator=ComparisonOperator.Equals,
        field_path="is_vegetarian",
        description="Validate that the recipe is truly vegetarian",
    )
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
    assertion=TraceAssertion.span_count(filter=SpanFilter.by_name("predict_endpoint")),
    operator=ComparisonOperator.Equals,
    expected_value=1,
)


tasks: list[LLMJudgeTask | AssertionTask | TraceAssertionTask] = [
    llm_judge_task,
    has_directions,
    trace_task,
]
