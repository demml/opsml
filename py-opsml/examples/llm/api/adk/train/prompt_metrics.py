# The following code defines the prompt metrics that will run in opsml and scouter


from opsml.scouter.alert import AlertThreshold
from opsml.scouter.drift import LLMMetric
from opsml.llm import Prompt, Score


def create_shipment_id_extraction_evaluation_prompt() -> Prompt:
    """
    Builds a prompt for evaluating how well the LLM extracted the shipment ID from the user's query.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the shipment ID extraction.

    Example:
        >>> prompt = create_shipment_id_extraction_evaluation_prompt()
    """
    return Prompt(
        user_message=(
            "You are an expert evaluator of shipment ID extraction. "
            "Given the original user query and the LLM's extracted shipment ID (in JSON format), assess how accurately and reliably the LLM identified the shipment ID.\n"
            "Consider the following criteria:\n"
            "- Is the extracted shipment ID correct and matches the user's query?\n"
            "- Is the JSON format correct (e.g., {'id': <shipment_id>} or {'id': null})?\n"
            "- Is the extraction robust to different query phrasings?\n"
            "- Is the extraction unambiguous and complete?\n\n"
            "Provide your evaluation as a JSON object with the following attributes:\n"
            "- score: An integer from 1 (poor) to 5 (excellent) indicating the quality of the extraction.\n"
            "- reason: A brief explanation for your score.\n\n"
            "Format your response as:\n"
            "{\n"
            '  "score": <integer 1-5>,\n'
            '  "reason": "<your explanation>"\n'
            "}\n\n"
            "Original Query:\n"
            "${user_query}\n\n"
            "Extracted Shipment ID (JSON):\n"
            "${extracted_shipment_id}\n\n"
            "Evaluation:"
        ),
        model="gemini-2.5-flash-lite-preview-06-17",
        provider="gemini",
        response_format=Score,
    )


def create_helpful_response_evaluation_prompt() -> Prompt:
    """
    Builds a prompt for evaluating how helpful and clear the LLM's response is to the user about shipment delivery.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the helpfulness of the response.

    Example:
        >>> prompt = create_helpful_response_evaluation_prompt()
    """
    return Prompt(
        user_message=(
            "You are an expert evaluator of assistant responses for supply chain operations. "
            "Given the original user query and the LLM's response about shipment delivery, assess how helpful, clear, and informative the response is.\n"
            "Consider the following criteria:\n"
            "- Does the response clearly communicate the estimated delivery time?\n"
            "- Is the response friendly and easy to understand?\n"
            "- Does it include relevant context (delays, current location, etc.)?\n"
            "- Is the information accurate and complete?\n\n"
            "Provide your evaluation as a JSON object with the following attributes:\n"
            "- score: An integer from 1 (not helpful) to 5 (very helpful) indicating the overall helpfulness of the response.\n"
            "- reason: A brief explanation for your score.\n\n"
            "Format your response as:\n"
            "{\n"
            '  "score": <integer 1-5>,\n'
            '  "reason": "<your explanation>"\n'
            "}\n\n"
            "Original Query:\n"
            "${user_query}\n\n"
            "LLM Response:\n"
            "${shipment_response}\n\n"
            "Evaluation:"
        ),
        model="gemini-2.5-flash-lite-preview-06-17",
        provider="gemini",
        response_format=Score,
    )


id_extraction = LLMMetric(
    name="id_extraction",
    prompt=create_shipment_id_extraction_evaluation_prompt(),
    value=5.0,
    alert_threshold_value=2.0,
    alert_threshold=AlertThreshold.Below,
)
helpful_response = LLMMetric(
    name="helpful_response",
    prompt=create_helpful_response_evaluation_prompt(),
    value=5.0,
    alert_threshold_value=2.0,
    alert_threshold=AlertThreshold.Above,
)
