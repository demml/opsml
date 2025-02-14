class OpsmlTestServer:
    def __init__(self, cleanup: bool = True) -> None:
        """Instantiates the test server."""

    def start_server(self) -> None:
        """Starts the test server."""

    def stop_server(self) -> None:
        """Stops the test server."""

    def __enter__(self) -> "OpsmlTestServer":
        """Starts the test server."""

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Stops the test server."""
