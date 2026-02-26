from agent.lifespan import prompts
from google.adk.agents.llm_agent import Agent


from google.adk.agents.callback_context import CallbackContext
from typing import Optional, cast
from google.genai import types  # For types.Content
from opentelemetry import trace
from opsml.scouter.tracing import ActiveSpan


def before_preference_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs entry into the preference analyzer agent and checks 'add_initial_note' in session state.
    If True, returns new Content to *replace* the agent's original instruction.
    If False or not present, returns None, allowing the agent's original instruction to be used.
    """

    tracer = trace.get_tracer("before_preference_callback")
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    print("Preference keys: ", current_state.keys())

    with cast(
        ActiveSpan, tracer.start_as_current_span("before_preference_callback")
    ) as span:
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("invocation.id", invocation_id)
        span.set_attribute("state", current_state)

    return None


def get_listening_history(user_id: str = "demo_user") -> dict:
    """Retrieves user's recent listening history from streaming service."""
    return {
        "status": "success",
        "user_id": user_id,
        "recent_tracks": [
            {
                "artist": "The Beatles",
                "song": "Here Comes The Sun",
                "genre": "classic rock",
            },
            {"artist": "Fleetwood Mac", "song": "Dreams", "genre": "classic rock"},
            {
                "artist": "Tame Impala",
                "song": "The Less I Know The Better",
                "genre": "psychedelic rock",
            },
        ],
        "top_genres": ["classic rock", "indie rock", "psychedelic"],
        "listening_patterns": {
            "peak_hours": ["evening"],
            "avg_session_duration": "45 minutes",
        },
    }


preference_analyzer = Agent(
    model=prompts.preference.prompt.model,
    name="PreferenceAnalyzer",
    description="Extracts musical preferences from user input and listening history.",
    instruction=prompts.preference.prompt.messages[0].text,
    tools=[get_listening_history],
    output_key="user_preferences",
    before_agent_callback=before_preference_callback,
)
