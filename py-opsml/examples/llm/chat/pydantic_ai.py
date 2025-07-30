from pydantic_ai import Agent
from opsml import PromptCard, Prompt, CardRegistry, RegistryType

# Creating the card here for demonstration purposes
# In practice, you would create the card, register it and then load it from the registry
# whenever you need it for your application.
card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="openai:gpt-4o",
        system_message="Be concise, reply with one sentence.",
    ),
)

agent = Agent(
    card.prompt.model,
    system_message=card.prompt.system_message[0].unwrap(),
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.data)

registry = CardRegistry(RegistryType.Prompt)
registry.register_card(card)
