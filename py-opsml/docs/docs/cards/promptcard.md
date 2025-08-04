`PromptCards` are used to store and standardize prompts for LLM workflows. They are built to be agnostic of a specific framework so that you can use them as you see fit. LLM tool is constantly changing and our goal is to not lock you in, but enable you to use your prompts wherever you see fit.

### GenAI 
``` py { title="GenAI - OpenAI" }
from openai import OpenAI
from opsml import PromptCard, Prompt, CardRegistry

client = OpenAI()

card = PromptCard(
    space="opsml",
    name="my_prompt",
    prompt=Prompt(
        model="gpt-4o",
        provider="openai",
        message="Provide a brief summary of the programming language $1.",
        system_instruction="Be concise, reply with one sentence.",
    ),
)

def chat_app(language: str):

    # create the prompt and bind the context
    user_prompt = card.prompt.message[0].bind(language).unwrap()

    response = client.chat.completions.create(
        model=card.prompt.model_identifier,
        messages=[
            {"role": "system", "content": user_prompt},
            {"role": "user", "content": card.prompt.message[0].unwrap()},
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
| <span class="text-alert">**prompt**</span>       | A list of messages (more on this below)  |
| <span class="text-alert">**model**</span>  | An optional model to use (e.g. "gpt-4o") |
| <span class="text-alert">**provider**</span>  | An optional provider to use (e.g. "openai") |
| <span class="text-alert">**system_prompt**</span>    | Optional system prompt to use (e.g. "Be concise") |
| <span class="text-alert">**sanitization_config**</span>    | Optional sanitization config to use. This can be used to detect common issues (e.g. sql injection) |
| <span class="text-alert">**model_setting**</span>    | Optional model settings to use. This can be used to set the model settings (e.g. temperature, max_tokens) |

**Note** - Either `model` and `provider` or `model_settings` must be provided


### Prompt Message

The prompt argument of the prompt class follows openai's message format. The following are the available message types:

- <span class="text-secondary">**String**</span>: A string message. (e.g. "Hello, world!")
- <span class="text-secondary">**StringList**</span>: A list of string messages. (e.g. ["Hello, world!", "How are you?"])
- <span class="text-secondary">**Message**</span>: A Message class object. See the Message class definition below.
- <span class="text-secondary">**MessageList**</span>: A list of Message class objects. See the Message class definition below.
- <span class="text-secondary">**AudioUrl**</span>: A class object that represents an audio url. 
- <span class="text-secondary">**ImageUrl**</span>: A class object that represents an image url.
- <span class="text-secondary">**DocumentUrl**</span>: A class object that represents a document url.
- <span class="text-secondary">**BinaryContent**</span>: A class object that represents binary content.

### Definitions 

The same arguments all apply to `system_prompt`

???success "Prompt"
    ```python
    class Prompt:
        def __init__(
            self,
            prompt: str | Sequence[str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl] | Message | List[Message],
            model: Optional[str] = None,
            provider: Optional[str] = None,
            system_prompt: Optional[str | List[str]] = None,
            sanitization_config: Optional[SanitizationConfig] = None,
            model_settings: Optional[ModelSettings] = None,
        ) -> None:
            """Prompt for interacting with an LLM API.

            Args:
                prompt (str | Sequence[str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl] | Message | List[Message]):
                    The prompt to use.
                model (str | None):
                    The model to use for the prompt. Required if model_settings is not provided.
                provider (str | None):
                    The provider to use for the prompt. Required if model_settings is not provided.
                system_prompt (Optional[str, Sequence[str]]):
                    The system prompt to use in the prompt.
                sanitization_config (None):
                    The santization configuration to use for the prompt.
                    Defaults to None which means no sanitization will be done
                model_settings (None):
                    The model settings to use for the prompt.
                    Defaults to None which means no model settings will be used
            """

        @property
        def model(self) -> str:
            """The model to use for the prompt."""

        @property
        def provider(self) -> str:
            """The provider to use for the prompt."""

        @property
        def model_identifier(self) -> Any:
            """Concatenation of provider and model, used for identifying the model in the prompt. This
            is commonly used with pydantic_ai to identify the model to use for the agent.

            Example:
                ```python
                    prompt = Prompt(
                        model="gpt-4o",
                        message="My prompt $1 is $2",
                        system_instruction="system_prompt",
                        provider="openai",
                    )
                    agent = Agent(
                        prompt.model_identifier, # "openai:gpt-4o"
                        system_instruction=prompt.system_instruction[0].unwrap(),
                    )
                ```
            """

        @property
        def model_settings(self) -> Dict[str, Any]:
            """The model settings to use for the prompt."""

        @property
        def sanitizer(self) -> PromptSanitizer:
            """The prompt sanitizer to use for the prompt."""

        @property
        def message(
            self,
        ) -> List[Message]:
            """The user prompt to use in the prompt."""

        @property
        def system_instruction(self) -> List[Message]:
            """The system prompt to use in the prompt."""

        def save_prompt(self, path: Optional[Path] = None) -> None:
            """Save the prompt to a file.

            Args:
                path (Optional[Path]):
                    The path to save the prompt to. If None, the prompt will be saved to
                    the current working directory.
            """

        @staticmethod
        def from_path(path: Path) -> "Prompt":
            """Load a prompt from a file.

            Args:
                path (Path):
                    The path to the prompt file.

            Returns:
                Prompt:
                    The loaded prompt.
            """

        @staticmethod
        def model_validate_json(json_string: str) -> "Prompt":
            """Validate the model JSON.

            Args:
                json_string (str):
                    The JSON string to validate.
            Returns:
                Prompt:
                    The prompt object.
            """

        def model_dump_json(self) -> str:
            """Dump the model to a JSON string.

            Returns:
                str:
                    The JSON string.
            """

        def __str__(self): ...
    ```

???success "Message"
    ```python
    class Message:
        def __init__(self, content: str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl) -> None:
            """Create a Message object.

            Args:
                content (str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl):
                    The content of the message.
            """

        @property
        def content(self) -> str | ImageUrl | AudioUrl | BinaryContent | DocumentUrl:
            """The content of the message"""

        @property
        def sanitized_output(self) -> Optional[SanitizedResult]:
            """The sanitized content of the message"""

        def bind(self, context: str) -> "Message":
            """Bind a context in the prompt. This is an immutable operation meaning that it
            will return a new Message object with the context bound.

                Example with Prompt that contains two messages

                ```python
                    prompt = Prompt(
                        model="openai:gpt-4o",
                        message=[
                            "My prompt $1 is $2",
                            "My prompt $3 is $4",
                        ],
                        system_instruction="system_prompt",
                    )
                    bounded_prompt = prompt.message[0].bind("world").unwrap() # we bind "world" to the first message
                ```

            Args:
                context (str):
                    The context to bind.

            Returns:
                Message:
                    The message with the context bound.
            """

        def sanitize(self, sanitizer: PromptSanitizer) -> "Message":
            """Sanitize the message content.

            Example with Prompt that contains two messages

                ```python
                    prompt = Prompt(
                        model="openai:gpt-4o",
                        message=[
                            "My prompt $1 is $2",
                            "My prompt $3 is $4",
                        ],
                        system_instruction="system_prompt",
                    )

                    # sanitize the first message
                    # Note: sanitization will fail if no sanitizer is provided (either through prompt.sanitizer or standalone)

                    # we bind "world" to the first message
                    bounded_prompt = prompt.message[0].bind("world").sanitize(prompt.sanitizer).unwrap()
                ```

            Args:
                sanitizer (PromptSanitizer):
                    The sanitizer to use for sanitizing the message

            Returns:
                Message:
                    The sanitized message.
            """

        def unwrap(self) -> Any:
            """Unwrap the message content to python compatible content.

            Returns:
                str:
                    The unwrapped message content.
            """
    ```

???success "AudioUrl"
    ```python
    class AudioUrl:
        def __init__(
            self,
            url: str,
            kind: Literal["audio-url"] = "audio-url",
        ) -> None:
            """Create an AudioUrl object.

            Args:
                url (str):
                    The URL of the audio.
                kind (Literal["audio-url"]):
                    The kind of the content.
            """
        @property
        def url(self) -> str:
            """The URL of the audio."""

        @property
        def kind(self) -> str:
            """The kind of the content."""

        @property
        def media_type(self) -> str:
            """The media type of the audio URL."""

        @property
        def format(self) -> str:
            """The format of the audio URL."""
    ```

???success "ImageUrl"
    ``python
    class ImageUrl:
        def __init__(
            self,
            url: str,
            kind: Literal["image-url"] = "image-url",
        ) -> None:
            """Create an ImageUrl object.

            Args:
                url (str):
                    The URL of the image.
                kind (Literal["image-url"]):
                    The kind of the content.
            """

        @property
        def url(self) -> str:
            """The URL of the image."""

        @property
        def kind(self) -> str:
            """The kind of the content."""

        @property
        def media_type(self) -> str:
            """The media type of the image URL."""

        @property
        def format(self) -> str:
            """The format of the image URL."""
    ```

???success "DocumentUrl"
    ```python
    class DocumentUrl:
        def __init__(
            self,
            url: str,
            kind: Literal["document-url"] = "document-url",
        ) -> None:
            """Create a DocumentUrl object.

            Args:
                url (str):
                    The URL of the document.
                kind (Literal["document-url"]):
                    The kind of the content.
            """

        @property
        def url(self) -> str:
            """The URL of the document."""

        @property
        def kind(self) -> str:
            """The kind of the content."""

        @property
        def media_type(self) -> str:
            """The media type of the document URL."""

        @property
        def format(self) -> str:
            """The format of the document URL."""
    ```

???success "BinaryContent"
    ```python
    class BinaryContent:
        def __init__(
            self,
            data: bytes,
            media_type: str,
            kind: str = "binary",
        ) -> None:
            """Create a BinaryContent object.

            Args:
                data (bytes):
                    The binary data.
                media_type (str):
                    The media type of the binary data.
                kind (str):
                    The kind of the content
            """

        @property
        def media_type(self) -> str:
            """The media type of the binary content."""

        @property
        def format(self) -> str:
            """The format of the binary content."""

        @property
        def data(self) -> bytes:
            """The binary data."""

        @property
        def kind(self) -> str:
            """The kind of the content."""
    ```