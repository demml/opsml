from opsml.registry.types import StorageRequest, StorageSystem
from opsml.registry.storage import client
from opsml.registry.sql.registry import CardRegistry


class Downloader:
    def __init__(self, storage_request: StorageRequest):
        self.storage_request = storage_request

    def get_path_from_uris(self) -> str:
        """Retries uri path from registry"""

        registry = CardRegistry(
            self.storage_request.registry_type,
        ).list_cards(uid=self.storage_request.card_uid)[0]

        uris = registry.get("uris")
        assert uris is not None, "URIs not found in registry"

        path: str = uris.get(self.storage_request.uri_name)
        assert path is not None, f"URI {self.storage_request.uri_name} not found in registry"

        return path

    def download(self, lpath: str) -> str:
        """Download artifact from storage"""

        # path may be injected when loading Cards from load_card method
        if self.storage_request.uri_path is not None:
            path = self.storage_request.uri_path

        # if no path is provided, get path from registry (most cases)
        else:
            # get path from registry
            path = self.get_path_from_uris()

        # no need to download if using local storage client
        if client.storage_client.backend == StorageSystem.LOCAL:
            return path

        files = client.storage_client.list_files(path)

        # download via any other filesystem or api client
        return client.storage_client.download(
            rpath=path,
            lpath=lpath,
            recursive=False,
            **{"files": files},
        )
