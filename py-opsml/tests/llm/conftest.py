from opsml.llm import Prompt, Score
import pytest


@pytest.fixture
def reformulation_evaluation_prompt():
    """
    Builds a prompt for evaluating the quality of a reformulated query.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the reformulation.

    Example:
        >>> prompt = create_reformulation_evaluation_prompt()
    """
    return Prompt(
        message=(
            "You are an expert evaluator of search query reformulations. "
            "Given the original user query and its reformulated version, your task is to assess how well the reformulation improves the query. "
            "Consider the following criteria:\n"
            "- Does the reformulation make the query more explicit and comprehensive?\n"
            "- Are relevant synonyms, related concepts, or specific features added?\n"
            "- Is the original intent preserved without changing the meaning?\n"
            "- Is the reformulation clear and unambiguous?\n\n"
            "Provide your evaluation as a JSON object with the following attributes:\n"
            "- score: An integer from 1 (poor) to 5 (excellent) indicating the overall quality of the reformulation.\n"
            "- reason: A brief explanation for your score.\n\n"
            "Format your response as:\n"
            "{\n"
            '  "score": <integer 1-5>,\n'
            '  "reason": "<your explanation>"\n'
            "}\n\n"
            "Original Query:\n"
            "${user_query}\n\n"
            "Reformulated Query:\n"
            "${response}\n\n"
            "Evaluation:"
        ),
        model="gemini-2.5-flash-lite-preview-06-17",
        provider="gemini",
        response_format=Score,
    )


@pytest.fixture
def relevancy_evaluation_prompt():
    """
    Builds a prompt for evaluating the relevance of a search query.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the query's relevance.

    Example:
        >>> prompt = create_relevancy_evaluation_prompt()
    """
    return Prompt(
        message=(
            "You are an expert evaluator of search query relevance. "
            "Given a user query, your task is to assess its relevance to the information needs of the user. "
            "Consider the following criteria:\n"
            "- Does the query contain relevant keywords and concepts?\n"
            "- Is the query clear and unambiguous?\n"
            "- Does the query adequately express the user's intent?\n\n"
            "Provide your evaluation as a JSON object with the following attributes:\n"
            "- score: An integer from 1 (poor) to 5 (excellent) indicating the overall relevance of the query.\n"
            "- reason: A brief explanation for your score.\n\n"
            "Format your response as:\n"
            "{\n"
            '  "score": <integer 1-5>,\n'
            '  "reason": "<your explanation>"\n'
            "}\n\n"
            "User Query:\n"
            "${user_query}\n\n"
            "Evaluation:"
        ),
        model="gemini-2.5-flash-lite-preview-06-17",
        provider="gemini",
        response_format=Score,
    )
