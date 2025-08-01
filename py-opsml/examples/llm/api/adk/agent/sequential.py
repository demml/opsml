from google.adk.agents import LlmAgent, SequentialAgent
from .callback import modify_output_after_agent


assistant_agent = LlmAgent(
    name="my_app",
    model="gemini-2.5-flash",
    description="Gemini agent",
    instruction="You are a helpful assistant.",
    after_agent_callback=modify_output_after_agent,
)


code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[assistant_agent],
    description="Executes a sequence of getting user input",
    # The agents will run in the order provided: Writer -> Reviewer -> Refactorer
)

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = assistant_agent
