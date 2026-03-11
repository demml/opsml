from agent.lifespan import prompts
from google.adk.agents.callback_context import CallbackContext
from typing import Optional
from google.adk.models.llm_response import LlmResponse
from opentelemetry import trace
from opsml.scouter.tracing import ActiveSpan
from opsml.scouter.evaluate import GenAIEvalRecord
from typing import cast


def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """Example of an after_agent_callback that could be used to log or process the output of the vegan_recipe_agent."""

    tracer = trace.get_tracer("response_callback")
    with cast(ActiveSpan, tracer.start_as_current_span("response_evaluation")) as span:
        content = llm_response.content

        if content and content.parts:
            span.add_queue_item(
                "response_eval",
                GenAIEvalRecord(
                    context={"response": content.parts[0].text},
                    session_id=callback_context.session.id,
                ),
            )

        else:
            span.set_status(
                "ERROR",
                "No content in LLM response or content has no parts",
            )

    return None
