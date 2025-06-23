# pylint: disable=dangerous-default-value
# type: ignore

from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..card import CardDeck
from ..scouter.client import HTTPConfig
from ..scouter.queue import KafkaConfig, RabbitMQConfig, RedisConfig, ScouterQueue

class AppState:
    """OpsML application state object. This is typically used in API
    workflows where you wish create a shared state to share among all requests.
    The OpsML app state provides a convenient way to load and store artifacts.
    Most notably, it provides an integration with Scouter so that you can load a `CardDeck`
    along with a `ScouterQueue` for drift detection. Future iterations of this class may
    include other convenience methods that simplify common API tasks.
    """

    def __init__(
        self,
        deck: CardDeck,
        queue: Optional[ScouterQueue] = None,
    ):
        """
        Initialize the AppState with a CardDeck and a ScouterQueue.

        Args:
            deck (CardDeck):
                The card deck containing Cards.
            queue (ScouterQueue):
                The Scouter queue for drift detection.
        """

    @staticmethod
    def from_path(
        path: Path,
        load_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
        transport_config: Optional[
            Union[
                KafkaConfig,
                RabbitMQConfig,
                RedisConfig,
                HTTPConfig,
            ]
        ] = None,
    ) -> "AppState":
        """
        Load the AppState from a file path.

        Args:
            path (str):
                The file path to load the AppState from. This is typically the path
                pointing to the directory containing the `CardDeck`.
            load_kwargs (Dict[str, Dict[str, Any]]):
                Optional kwargs for loading cards. Expected format:
                {
                    "card_alias": {
                        "interface": interface_object,
                        "load_kwargs": DataLoadKwargs | ModelLoadKwargs
                    }
                }
            transport_config (Union[KafkaConfig, RabbitMQConfig, RedisConfig, HTTPConfig]) | None:
                Optional transport configuration for the queue publisher
                Can be KafkaConfig, RabbitMQConfig RedisConfig, or HTTPConfig. If not provided,
                the queue will not be initialized.

        Example:
            ```python
            from opsml.app import AppState
            from opsml.scouter import KafkaConfig

            app_state = AppState.from_path(
                "/path/to/card_deck",
                transport_config=KafkaConfig(),
                )

            # Access the card deck and queue
            deck = app_state.deck
            queue = app_state.queue
            ```

        Returns:
            AppState: The loaded AppState.
        """

    @property
    def deck(self) -> CardDeck:
        """Get the card deck."""

    @property
    def queue(self) -> ScouterQueue:
        """Get the Scouter queue."""
