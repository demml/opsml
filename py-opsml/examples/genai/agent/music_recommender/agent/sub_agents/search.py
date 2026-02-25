from agent.lifespan import prompts
from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types  # For types.Content
from typing import Optional
from opentelemetry import trace
from typing import cast
from opsml.scouter.evaluate import GenAIEvalRecord
from opsml.scouter.tracing import ActiveSpan


def search_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """
    Logs exit from an agent and checks 'add_concluding_note' in session state.
    If True, returns new Content to *replace* the agent's original output.
    If False or not present, returns None, allowing the agent's original output to be used.
    """

    tracer = trace.get_tracer("after_search_callback")
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state = callback_context.state.to_dict()

    with cast(ActiveSpan, tracer.start_as_current_span("search_callback")) as span:
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("invocation.id", invocation_id)

        queue_record = GenAIEvalRecord(
            context={
                "candidate_tracks": current_state.get("candidate_tracks", {}),
            },
        )

        span.add_queue_item("search", queue_record)

    return None


def search_music_catalog(genre: str = "", mood: str = "", era: str = "") -> dict:
    """Searches music catalog with genre, mood, and era filters."""
    return {
        "status": "success",
        "filters_applied": {"genre": genre, "mood": mood, "era": era},
        "results": [
            {
                "artist": "Bob Seger",
                "song": "Night Moves",
                "genre": "classic rock",
                "era": "1970s",
                "mood": "nostalgic",
            },
            {
                "artist": "Neil Young",
                "song": "Harvest Moon",
                "genre": "folk rock",
                "era": "1990s",
                "mood": "mellow",
            },
            {
                "artist": "Khruangbin",
                "song": "Time (You and I)",
                "genre": "psychedelic",
                "era": "2020s",
                "mood": "relaxing",
            },
        ],
    }


def calculate_similarity(track_name: str, reference_genre: str = "") -> dict:
    """Scores how well a track matches user's historical preferences."""
    return {
        "track": track_name,
        "similarity_score": 0.82,
        "reasoning": "Strong match on melodic structure and tempo",
        "confidence": "high",
    }


search_specialist = Agent(
    model=prompts.search.prompt.model,
    name="SearchSpecialist",
    description="Finds candidate tracks based on pattern analysis.",
    instruction=prompts.search.prompt.messages[0].text,
    tools=[search_music_catalog, calculate_similarity],
    output_key="candidate_tracks",  # Reads search_strategy, writes candidates
)
