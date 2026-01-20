`PromptCards` are used to store and standardize prompts for LLM workflows. They are built to be agnostic of a specific framework so that you can use them as you see fit. LLM tool is constantly changing and our goal is to not lock you in, but enable you to use your prompts wherever you see fit.

The following shows how to use a `PromptCard` with OpenAI's [API](https://platform.openai.com/docs/libraries)

``` py { title="GenAI - OpenAI" }
from openai import OpenAI
from opsml import PromptCard, Prompt, CardRegistry

client = OpenAI()

card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(  # (1)
        model="gpt-4o",
        provider="openai",
        messages="Provide a brief summary of the programming language ${language}.", 
        system_instructions="Be concise, reply with one sentence.",
    ),
)

def chat_app(language: str):

    # create the prompt and bind the context
    user_prompt = card.prompt.bind(language=language).messages[0]
    system_instruction = card.prompt.system_instruction[0]

    response = client.chat.completions.create(
        model=card.prompt.model_identifier,
        messages=[
            system_instruction.model_dump()
            user_prompt.model_dump()
        ],
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    result = chat_app("Python")
    print(result)

    # Register the card in the registry
    registry = CardRegistry("prompt")
    registry.register_card(card)

# This code will run as is
```

1. The `message` argument of the `Prompt` class can be a string or a list of strings. In this case, we are using a single string with a placeholder `${language}` that will be replaced with the actual value when the prompt is bound via the `bind` method. This allows you to create dynamic prompts that can be reused with different inputs.


In a typical development workflow, you would develop and test different prompts depending on your use case. Whenever a prompt is ready for production, you can register it in the `PromptCard` registry and load/use it in your application. This way, you can keep track of all the prompts you have developed and their versions, making it easier to manage and update them as needed. In addition, in workflows that require multiple prompts, you can leverage opsml's `ServiceCard` feature to build a service of prompt cards.

### How it all works

As you can tell in the example above, `PromptCards` are created by passing in a `Prompt`, some required args and some optional args. The `Prompt` is a framework agnostic class that can hold one or more user messages, system prompts and model settings.

### Loading a PromptCard

You can load a `PromptCard` as you would any other card in the registry.

``` python
from opsml import CardRegistry, RegistryType

registry = CardRegistry(RegistryTYpe.Prompt)

card = registry.load_card(uid="{{card uid}}")

# or

card = registry.load_card(space="opsml", name="my_prompt")
```

## Prompt
The `Prompt` class is the core of the `PromptCard`. It is used to define the prompt that will be used in the LLM workflow. The `Prompt` class has the following attributes:

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**message**</span>       | A list of messages (more on this below)  |
| <span class="text-alert">**model**</span>  | An optional model to use (e.g. "gpt-4o") |
| <span class="text-alert">**provider**</span>  | An optional provider to use (e.g. "openai") |
| <span class="text-alert">**system_instruction**</span>    | Optional system prompt to use (e.g. "Be concise") |
| <span class="text-alert">**model_setting**</span>    | Optional model settings to use. This can be used to set the model settings (e.g. temperature, max_tokens) |


### Prompt Message

The message argument of the prompt class follows openai's message format. The following are the available message types:

- <span class="text-secondary">**String**</span>: A string message. (e.g. "Hello, world!")
- <span class="text-secondary">**StringList**</span>: A list of string messages. (e.g. ["Hello, world!", "How are you?"])
- <span class="text-secondary">**Message**</span>: A Message class object. See the Message class definition below.
- <span class="text-secondary">**MessageList**</span>: A list of Message class objects. See the Message class definition below.
- <span class="text-secondary">**AudioUrl**</span>: A class object that represents an audio url. 
- <span class="text-secondary">**ImageUrl**</span>: A class object that represents an image url.
- <span class="text-secondary">**DocumentUrl**</span>: A class object that represents a document url.
- <span class="text-secondary">**BinaryContent**</span>: A class object that represents binary content.
