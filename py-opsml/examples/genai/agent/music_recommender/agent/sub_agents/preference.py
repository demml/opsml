from agent.lifespan import prompts
from google.adk.agents.llm_agent import Agent


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
    output_key="user_preferences",  # Stores result in shared state
)
