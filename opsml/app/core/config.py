import os

BASE_LOCAL_SQL = f"sqlite:///{os.path.expanduser('~')}/opsml_database.db"


class MlFlowConfig:
    # Mlflow
    MLFLOW_SERVER_ARTIFACT_DESTINATION = os.getenv("_MLFLOW_SERVER_ARTIFACT_DESTINATION", "./mlruns")
    MLFLOW_SERVER_ARTIFACT_ROOT = os.getenv("_MLFLOW_SERVER_ARTIFACT_ROOT", "mlflow-artifacts:/")
    MLFLOW_SERVER_FILE_STORE = os.getenv("_MLFLOW_SERVER_FILE_STORE", BASE_LOCAL_SQL)
    MLFLOW_SERVER_SERVE_ARTIFACTS = bool(os.getenv("_MLFLOW_SERVER_SERVE_ARTIFACTS", "true"))


class OpsmlConfig:
    APP_NAME = "OPSML-API"
    APP_ENV = os.environ.get("APP_ENV", "development")
    STORAGE_URI = os.environ.get("OPSML_STORAGE_URI", "./mlruns")
    TRACKING_URI = os.environ.get("OPSML_TRACKING_URI", BASE_LOCAL_SQL)

    def __init__(self):
        self._proxy_root = os.environ.get("PROXY_ROOT")
        self._is_proxy = False

    @property
    def proxy_root(self):
        return self._proxy_root

    @proxy_root.setter
    def proxy_root(self, root: str):
        self._proxy_root = root

    @property
    def is_proxy(self):
        return self._is_proxy

    @is_proxy.setter
    def is_proxy(self, proxy: bool):
        self._is_proxy = proxy


config = OpsmlConfig()
