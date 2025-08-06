from openai import OpenAI
from opsml import PromptCard, Prompt, CardRegistry

client = OpenAI()

card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="o4-mini",
        provider="openai",
        message="Provide a brief summary of the programming language ${language}.",
        system_instruction="Be concise, reply with one sentence.",
    ),
)


def chat_app(language: str):
    # create the prompt and bind the context
    user_message = card.prompt.bind(language=language).message[0].unwrap()
    system_instruction = card.prompt.system_instruction[0].unwrap()

    response = client.responses.create(
        model=card.prompt.model,
        instructions=system_instruction,
        input=user_message,
    )

    return response.output_text


if __name__ == "__main__":
    result = chat_app("Python")
    print(result)

    # Register the card in the registry
    registry = CardRegistry("prompt")
    registry.register_card(card)
