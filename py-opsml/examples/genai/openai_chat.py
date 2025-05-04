from openai import OpenAI
from opsml import PromptCard, Prompt, CardRegistry

client = OpenAI()

card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="gpt-4o",
        prompt="Provide a brief summary of the programming language $1.",
        system_prompt="Be concise, reply with one sentence.",
    ),
)


def chat_app(language: str):
    user_prompt = card.prompt.prompt[0].bind(language).unwrap()

    response = client.chat.completions.create(
        model=card.prompt.model,
        messages=[
            {"role": "system", "content": user_prompt},
            {"role": "user", "content": card.prompt.prompt[0].unwrap()},
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    result = chat_app("Python")
    print(result)

    # Register the card in the registry
    registry = CardRegistry("prompt")
    registry.register_card(card)
