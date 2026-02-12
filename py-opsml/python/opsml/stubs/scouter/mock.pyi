#### begin imports ####

import datetime
from pathlib import Path
from typing import List, Optional

from .tracing import TraceSpan

#### end of imports ####

class ScouterTestServer:
    def __init__(
        self,
        cleanup: bool = True,
        rabbit_mq: bool = False,
        kafka: bool = False,
        openai: bool = False,
        base_path: Optional[Path] = None,
    ) -> None:
        """Instantiates the test server.

        When the test server is used as a context manager, it will start the server
        in a background thread and set the appropriate env vars so that the client
        can connect to the server. The server will be stopped when the context manager
        exits and the env vars will be reset.

        Args:
            cleanup (bool, optional):
                Whether to cleanup the server after the test. Defaults to True.
            rabbit_mq (bool, optional):
                Whether to use RabbitMQ as the transport. Defaults to False.
            kafka (bool, optional):
                Whether to use Kafka as the transport. Defaults to False.
            openai (bool, optional):
                Whether to create a mock OpenAITest server. Defaults to False.
            base_path (Optional[Path], optional):
                The base path for the server. Defaults to None. This is primarily
                used for testing loading attributes from a pyproject.toml file.
        """

    def start_server(self) -> None:
        """Starts the test server."""

    def stop_server(self) -> None:
        """Stops the test server."""

    def __enter__(self) -> "ScouterTestServer":
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

class MockConfig:
    def __init__(self, **kwargs) -> None:
        """Mock configuration for the ScouterQueue

        Args:
            **kwargs: Arbitrary keyword arguments to set as attributes.
        """

def create_simple_trace() -> List["TraceSpan"]:
    """Creates a simple trace with a few spans.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

def create_nested_trace() -> List["TraceSpan"]:
    """Creates a nested trace with parent-child relationships.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

def create_trace_with_attributes() -> List["TraceSpan"]:
    """Creates a trace with spans that have attributes.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

def create_multi_service_trace() -> List["TraceSpan"]:
    """Creates a trace that spans multiple services.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

def create_sequence_pattern_trace() -> List["TraceSpan"]:
    """Creates a trace with a sequence pattern of spans.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """

def create_trace_with_errors() -> List["TraceSpan"]:
    """Creates a trace with spans that contain errors.

    Returns:
        List[TraceSpan]: A list of TraceSpan objects representing the trace.
    """
