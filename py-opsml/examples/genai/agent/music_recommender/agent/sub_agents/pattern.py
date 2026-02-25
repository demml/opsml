from agent.lifespan import prompts
from google.adk.agents.llm_agent import Agent


pattern_recognizer = Agent(
    model=prompts.pattern.prompt.model,
    name="PatternRecognizer",
    description="Identifies patterns and themes in user's musical taste.",
    instruction=prompts.pattern.prompt.messages[0].text,
    tools=[],
    output_key="search_strategy",  # Reads user_preferences, writes search_strategy
)
