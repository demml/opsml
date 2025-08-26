# pylint: disable=dangerous-default-value
# type: ignore

from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..card import ServiceCard
from ..scouter.client import HTTPConfig
from ..scouter.queue import KafkaConfig, RabbitMQConfig, RedisConfig, ScouterQueue

class ReloadConfig:
    """Reload configuation to use with an Opsml AppState object. Defines the reload logic
    for checking, downloading and reloading ServiceCards and ScouterQueues associated with
    an AppState
    """

    def __init__(
        self,
        cron: str,
        max_retries: int = 3,
        write_path: Optional[Path] = None,
    ):
        """Initialize the reload configuration.

        Args:
            cron (str):
                The cron expression for the reload schedule.
            max_retries (int):
                The maximum number of retries for loading the service card.
                Defaults to 3.
            write_path (Optional[Path]):
                The optional path to write the service card. Defaults to Path({current directory})/ service_reload
        """
        ...

    @property
    def cron(self) -> str:
        """Get the cron expression for the reload schedule."""

    @cron.setter
    def cron(self, value: str):
        """Set the cron expression for the reload schedule."""

class AppState:
    """OpsML application state object. This is typically used in API
    workflows where you wish create a shared state to share among all requests.
    The OpsML app state provides a convenient way to load and store artifacts.
    Most notably, it provides an integration with Scouter so that you can load a `ServiceCard`
    along with a `ScouterQueue` for drift detection. Future iterations of this class may
    include other convenience methods that simplify common API tasks.
    """

    @staticmethod
    def from_path(
        path: Path,
        transport_config: Optional[
            Union[
                KafkaConfig,
                RabbitMQConfig,
                RedisConfig,
                HTTPConfig,
            ]
        ] = None,
        reload_config: Optional[ReloadConfig] = None,
        load_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> "AppState":
        """
        Load the AppState from a file path.

        Args:
            path (str):
                The file path to load the AppState from. This is typically the path
                pointing to the directory containing the `ServiceCard`.

            transport_config (KafkaConfig | RabbitMQConfig | RedisConfig | HTTPConfig | None):
                Optional transport configuration for the queue publisher
                Can be KafkaConfig, RabbitMQConfig RedisConfig, or HTTPConfig. If not provided,
                the queue will not be initialized.

            load_kwargs (Dict[str, Dict[str, Any]]):
                Optional kwargs for loading cards. Expected format:
                {
                    "card_alias": {
                        "interface": interface_object,
                        "load_kwargs": DataLoadKwargs | ModelLoadKwargs
                    }
                }

        Example:
            ```python
            from opsml.app import AppState
            from opsml.scouter import KafkaConfig

            app_state = AppState.from_path(
                "/path/to/service",
                transport_config=KafkaConfig(),
                )

            # Access the service card and queue
            service = app_state.service
            queue = app_state.queue
            ```

        Returns:
            AppState: The loaded AppState.
        """

    @property
    def service(self) -> ServiceCard:
        """Get the service card."""

    @property
    def queue(self) -> ScouterQueue:
        """Get the Scouter queue."""

    @property
    def reloader_running(self) -> bool:
        """Check if the ServiceReloader is currently running."""

    def reload(self) -> None:
        """Forces `AppState` to check for new `ServiceCards` and reload if necessary."""

    def start_reloader(self) -> None:
        """Starts the `AppState` reloader."""

    def stop_reloader(self) -> None:
        """Stops the `AppState` reloader."""

    def shutdown(self) -> None:
        """Shuts down the `AppState` `ScouterQueue` and reloader if running.
        This is a destructive operation and will attempt to close all background threads
        associated with the `ScouterQueue` and reloader. Only use this method with graceful
        shutdown procedures in mind.
        """
