from openai import OpenAI
from opsml import CardRegistry, Prompt, PromptCard

client = OpenAI()

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
    user_message = card.prompt.messages[0].bind(language=language)
    system_instruction = card.prompt.system_instructions[0]

    response = client.responses.create(
        model=card.prompt.model,
        instructions=system_instruction.model_dump(),
        input=user_message.model_dump(),
    )

    return response.output_text


if __name__ == "__main__":
    result = chat_app("Python")
    print(result)

    # Register the card in the registry
    registry = CardRegistry("prompt")
    registry.register_card(card)
