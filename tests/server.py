from multiprocessing import Process
from opsml_artifacts.api.main import get_opsml_app
import uvicorn
import requests
import pytest
import time

session = requests.Session()


class TestApp:
    """Test the app class."""

    def __init__(self):
        self.url = "http://0.0.0.0:8000"

    def start(self):
        """Bring server up."""
        app = get_opsml_app()
        self.proc = Process(
            target=uvicorn.run,
            args=(app,),
            kwargs={"host": "0.0.0.0", "port": 8000, "log_level": "info"},
            daemon=True,
        )
        self.proc.start()

        running = False
        while not running:
            try:
                response = session.get(f"{self.url}/opsml/healthcheck")
                if response.status_code == 200:
                    running = True
            except Exception as error:
                time.sleep(2)
                pass

    def shutdown(self):
        """Shutdown the app."""
        self.proc.terminate()


@pytest.fixture(scope="function")
def test_server():
    test_app = TestApp()

    test_app.start()

    yield test_app

    test_app.shutdown()
