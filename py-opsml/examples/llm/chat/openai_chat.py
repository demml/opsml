from openai import OpenAI
from opsml import PromptCard, Prompt, CardRegistry

client = OpenAI()

card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="gpt-4o",
        message="Provide a brief summary of the programming language ${language}.",
        system_instruction="Be concise, reply with one sentence.",
    ),
)


def chat_app(language: str):
    response = client.chat.completions.create(
        model=card.prompt.model,
        messages=[
            {"role": "system", "content": card.prompt.system_instruction[0].unwrap()},
            {
                "role": "user",
                "content": card.prompt.bind(language=language).message[0].unwrap(),
            },
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    result = chat_app("Python")
    print(result)

    # Register the card in the registry
    registry = CardRegistry("prompt")
    registry.register_card(card)
