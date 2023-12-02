import argparse


def launch_uvicorn_app(login: bool = False, port: int = 8888):
    """
    Launches a Uvicorn Opsml server

    Args:
        run_mlflow:
            Whether to launch with mlflow
        login:
            Whether to use login credentials
        port:
            Default port to use with the opsml server
    """

    from opsml.app.main import OpsmlApp  # pylint: disable=import-outside-toplevel

    model_api = OpsmlApp(port=port, login=login)
    model_api.build_app()
    model_api.run()


def cli():
    parser = argparse.ArgumentParser(description="Launch opsml server")
    parser.add_argument("--login", type=bool, default=False, help="whether to use login credentials")
    parser.add_argument("--port", type=int, default=8888, help="port to use for opsml server")
    args = parser.parse_args()

    launch_uvicorn_app(login=args.login, port=args.port)
