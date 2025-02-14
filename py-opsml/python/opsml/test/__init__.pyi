class OpsmlTestServer:
    def __init__(self, cleanup: bool = True) -> None:
        """Instantiates the test server.

        When the test server is used as a context manager, it will start the server
        in a background thread and set the appropriate env vars so that the client
        can connect to the server. The server will be stopped when the context manager
        exits and the env vars will be reset.

        Args:
            cleanup (bool, optional): Whether to cleanup the server after the test.
            Defaults to True.
        """

    def start_server(self) -> None:
        """Starts the test server."""

    def stop_server(self) -> None:
        """Stops the test server."""

    def __enter__(self) -> "OpsmlTestServer":
        """Starts the test server."""

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Stops the test server."""
