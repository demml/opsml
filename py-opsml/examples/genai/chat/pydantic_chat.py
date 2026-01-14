from opsml import CardRegistry, Prompt, PromptCard, RegistryType
from pydantic_ai import Agent

card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="o4-mini",
        provider="openai",
        messages="Provide a brief summary of the programming language ${language}.",
        system_instructions="Be concise, reply with one sentence.",
    ),
)


def chat_app(language: str):
    # create the prompt and bind the context
    user_message = card.prompt.bind(language=language).messages[0]
    system_instruction = card.prompt.system_instructions[0]

    agent = Agent(
        model=card.prompt.model_identifier,  # using model identifier that concatenates provider and model
        system_prompt=system_instruction.text,
    )

    result = agent.run_sync(user_message.text)

    return result.output


if __name__ == "__main__":
    result = chat_app("Python")
    print(result)

    # Register the card in the registry
    registry = CardRegistry(RegistryType.Prompt)
    registry.register_card(card)
