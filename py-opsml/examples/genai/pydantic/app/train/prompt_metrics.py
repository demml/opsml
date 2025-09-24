# The following code defines the prompt metrics that will run in opsml and scouter


from opsml.genai import Prompt, Score
from opsml.scouter.alert import AlertThreshold
from opsml.scouter.drift import LLMDriftMetric

LLM_MODEL = "o4-mini"
LLM_PROVIDER = "openai"


def create_shipment_eta_task_evaluation_prompt() -> Prompt:
    """
    Builds a prompt for evaluating how well the LLM performed the full shipment ETA task:
    extracting the shipment ID, calling the tool, and formatting the response.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the LLM's task performance.

    Example:
        >>> prompt = create_shipment_eta_task_evaluation_prompt()
    """
    return Prompt(
        message="""
            You are an expert evaluator of supply chain assistant performance.
            Given the original user query, the LLM's tool call, and the LLM's final response, assess how well the LLM performed the following:
                - Correctly extracted the shipment ID from the user's query.
                - Correctly called the tool `get_shipment_eta_by_id` with the extracted shipment ID.
                - Correctly formatted the final response with ETA, shipment ID, destination, and shipment status.
            Consider:
                - Did the LLM extract the correct shipment ID?
                - Was the tool call correct and properly formatted?
                - Did the final response include all required fields and match the tool result?
                - Was the output clear and unambiguous?
            Provide your evaluation as a JSON object with the following attributes:
                - score: An integer from 1 (poor) to 5 (excellent) indicating the overall task performance.
                - reason: A brief explanation for your score.
            Format your response as:
            {
                "score": <integer 1-5>,
                "reason": "<your explanation>"
            }
            Original Query:
            ${user_query}
            Tool Call:
            ${tool_call}
            Tool Result:
            ${tool_result}
            LLM Response:
            ${llm_response}
            Evaluation:
        """,
        model=LLM_MODEL,
        provider=LLM_PROVIDER,
        response_format=Score,
    )


def create_shipment_eta_reply_evaluation_prompt() -> Prompt:
    """
    Builds a prompt for evaluating how well the LLM generated a user-facing reply
    from the structured shipment ETA information.

    Returns:
        Prompt: A prompt that asks for a JSON evaluation of the LLM's reply quality.

    Example:
        >>> prompt = create_shipment_eta_reply_evaluation_prompt()
    """
    return Prompt(
        message="""
            You are an expert evaluator of supply chain assistant responses.
            Given the structured shipment ETA information and the LLM's reply to the user, assess how well the LLM communicated the information.
            Consider the following:
                - Did the reply include all relevant details (ETA, shipment ID, destination, shipment status)?
                - Was the reply clear, friendly, and easy to understand?
                - Did the reply accurately reflect the provided shipment ETA information?
                - Was the output free of ambiguity or missing information?
            Provide your evaluation as a JSON object with the following attributes:
                - score: An integer from 1 (poor) to 5 (excellent) indicating the quality of the reply.
                - reason: A brief explanation for your score.
            Format your response as:
            {
                "score": <integer 1-5>,
                "reason": "<your explanation>"
            }
            Shipment ETA Information:
            ${shipment_eta_info}
            LLM Reply:
            ${llm_reply}
            Evaluation:
        """,
        model=LLM_MODEL,
        provider=LLM_PROVIDER,
        response_format=Score,
    )


shipment_eta_task_evaluation = LLMDriftMetric(
    name="shipment_eta_task_evaluation",
    prompt=create_shipment_eta_task_evaluation_prompt(),
    value=5.0,
    alert_threshold_value=2.0,
    alert_threshold=AlertThreshold.Below,
)

shipment_eta_reply_evaluation = LLMDriftMetric(
    name="shipment_eta_reply_evaluation",
    prompt=create_shipment_eta_reply_evaluation_prompt(),
    value=5.0,
    alert_threshold_value=2.0,
    alert_threshold=AlertThreshold.Below,
)
