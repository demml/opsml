if __name__ == "__main__":
    from openai import OpenAI
    from opsml import PromptCard, Prompt, CardRegistry

    client = OpenAI()

    card = PromptCard(
        space="opsml",
        name="my_prompt",
        prompt=Prompt(
            model="o4-mini",
            provider="openai",
            message="Provide a brief summary of the programming language ${language}.",  #
            system_instruction="Be concise, reply with one sentence.",
        ),
    )

    def chat_app(language: str):
        # create the prompt and bind the context
        user_message = card.prompt.bind(language=language).message[0].unwrap()
        system_instruction = card.prompt.system_instruction[0].unwrap()

        response = client.chat.completions.create(
            model=card.prompt.model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message},
            ],
        )

        return response.choices[0].message.content

    if __name__ == "__main__":
        result = chat_app("Python")
        print(result)

        # Register the card in the registry
        registry = CardRegistry("prompt")  #
        registry.register_card(card)

    # This code will run as is
