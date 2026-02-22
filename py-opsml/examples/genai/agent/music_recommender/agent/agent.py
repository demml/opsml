"""
Music Recommendation: Prompt Chaining with SequentialAgent

This demonstrates the Prompt Chaining pattern using Google ADK's SequentialAgent.
Each sub-agent performs one step and passes results via shared state using output_key.

Pipeline:
1. Preference Analyzer → Extracts user taste
2. Pattern Recognizer → Identifies listening themes
3. Search Specialist → Finds candidate tracks
4. Recommendation Generator → Produces final recommendations
"""

from agent.lifespan import prompts
from google.adk.agents.llm_agent import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.models.lite_llm import LiteLlm


def get_listening_history(user_id: str = "demo_user") -> dict:
    """Retrieves user's recent listening history from streaming service."""
    return {
        "status": "success",
        "user_id": user_id,
        "recent_tracks": [
            {"artist": "The Beatles", "song": "Here Comes The Sun", "genre": "classic rock"},
            {"artist": "Fleetwood Mac", "song": "Dreams", "genre": "classic rock"},
            {"artist": "Tame Impala", "song": "The Less I Know The Better", "genre": "psychedelic rock"},
        ],
        "top_genres": ["classic rock", "indie rock", "psychedelic"],
        "listening_patterns": {"peak_hours": ["evening"], "avg_session_duration": "45 minutes"},
    }


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
            {"artist": "Neil Young", "song": "Harvest Moon", "genre": "folk rock", "era": "1990s", "mood": "mellow"},
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


# ============================================================================
# STEP 1: Preference Analyzer Agent
# ============================================================================

preference_analyzer = Agent(
    model=LiteLlm(model="openai/google/gemini-2.5-flash"),
    name="PreferenceAnalyzer",
    description="Extracts musical preferences from user input and listening history.",
    instruction=prompts.preference.prompt.messages[0].text,
    tools=[get_listening_history],
    output_key="user_preferences",  # Stores result in shared state
)


# ============================================================================
# STEP 2: Pattern Recognizer Agent
# ============================================================================

pattern_recognizer = Agent(
    model=LiteLlm(model="openai/google/gemini-2.5-flash"),
    name="PatternRecognizer",
    description="Identifies patterns and themes in user's musical taste.",
    instruction=prompts.pattern.prompt.messages[0].text,
    tools=[],
    output_key="search_strategy",  # Reads user_preferences, writes search_strategy
)


# ============================================================================
# STEP 3: Search Specialist Agent
# ============================================================================

search_specialist = Agent(
    model=LiteLlm(model="openai/google/gemini-2.5-flash"),
    name="SearchSpecialist",
    description="Finds candidate tracks based on pattern analysis.",
    instruction=prompts.search.prompt.messages[0].text,
    tools=[search_music_catalog, calculate_similarity],
    output_key="candidate_tracks",  # Reads search_strategy, writes candidates
)


# ============================================================================
# STEP 4: Recommendation Generator Agent
# ============================================================================

recommendation_generator = Agent(
    model=LiteLlm(model="openai/google/gemini-2.5-flash"),
    name="RecommendationGenerator",
    description="Generates final personalized recommendations with reasoning.",
    instruction=prompts.recommendation.prompt.messages[0].text,
    tools=[],
    output_key="final_recommendations",  # Reads candidates, produces final output
)


# ============================================================================
# SEQUENTIAL AGENT (Orchestrator)
# ============================================================================

root_agent = SequentialAgent(
    name="MusicRecommenderChain",
    sub_agents=[preference_analyzer, pattern_recognizer, search_specialist, recommendation_generator],
    description="Chain-of-Thought music recommender using sequential agent pipeline.",
)
