from opsml.test import OpsmlTestServer


def test_server():
    server = OpsmlTestServer()
    server.start_server()

    server.stop_server()
