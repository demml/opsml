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
    user_message = card.prompt.bind(language=language).messages[0]
    system_instruction = card.prompt.system_instructions[0]

    response = client.chat.completions.create(
        model=card.prompt.model,
        messages=[
            {"role": "system", "content": system_instruction.text},
            {"role": "user", "content": user_message.text},
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    result = chat_app("Python")
    print(result)

    # Register the card in the registry
    registry = CardRegistry("prompt")
    registry.register_card(card)
