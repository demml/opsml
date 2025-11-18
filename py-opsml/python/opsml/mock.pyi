from pathlib import Path
from typing import Optional

class RegistryTestHelper:
    """Helper class for testing the registry"""

    def __init__(self) -> None: ...
    def setup(self) -> None: ...
    def cleanup(self) -> None: ...

class OpsmlTestServer:
    def __init__(self, cleanup: bool = True, base_path: Optional[Path] = None) -> None:
        """Instantiates the test server.

        When the test server is used as a context manager, it will start the server
        in a background thread and set the appropriate env vars so that the client
        can connect to the server. The server will be stopped when the context manager
        exits and the env vars will be reset.

        Args:
            cleanup (bool, optional):
                Whether to cleanup the server after the test. Defaults to True.
            base_path (Optional[Path], optional):
                The base path for the server. Defaults to None. This is primarily
                used for testing loading attributes from a pyproject.toml file.
        """

    def start_server(self) -> None:
        """Starts the test server."""

    def stop_server(self) -> None:
        """Stops the test server."""

    def __enter__(self) -> "OpsmlTestServer":
        """Starts the test server."""

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Stops the test server."""

    def set_env_vars_for_client(self) -> None:
        """Sets the env vars for the client to connect to the server."""

    def remove_env_vars_for_client(self) -> None:
        """Removes the env vars for the client to connect to the server."""

    @staticmethod
    def cleanup() -> None:
        """Cleans up the test server."""

class OpsmlServerContext:
    def __init__(self) -> None:
        """Instantiates the server context.
        This is helpful when you are running tests in server mode to
        aid in background cleanup of resources
        """

    def __enter__(self) -> "OpsmlServerContext":
        """Starts the server context."""

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Stops the server context."""

    @property
    def server_uri(self) -> str:
        """Returns the server URI."""

class MockConfig:
    def __init__(self, **kwargs) -> None:
        """Mock configuration for the ScouterQueue

        Args:
            **kwargs: Arbitrary keyword arguments to set as attributes.
        """

class LLMTestServer:
    """
    Mock server for OpenAI API.
    This class is used to simulate the OpenAI API for testing purposes.
    """

    def __init__(self): ...
    def __enter__(self):
        """
        Start the mock server.
        """

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stop the mock server.
        """
