from pydantic_ai import Agent
from opsml import PromptCard, Prompt, CardRegistry, RegistryType
from pydantic_ai.models.test import TestModel

# Creating the card here for demonstration purposes
# In practice, you would create the card, register it and then load it from the registry
# whenever you need it for your application.
card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="google-gla:gemini-1.5-flash",
        system_prompt="Be concise, reply with one sentence.",
    ),
)

agent = Agent(
    card.prompt.model,
    system_prompt=card.prompt.system_prompt[0],
)

with agent.override(model=TestModel()):
    result = agent.run_sync('Where does "hello world" come from?')
    print(result.data)


registry = CardRegistry(RegistryType.Prompt)
registry.register(card)
