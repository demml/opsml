from opsml.registry.types import StorageRequest, StorageSystem
from opsml.registry.storage import client
from opsml.registry.sql.registry import CardRegistry


class Downloader:
    def __init__(self, storage_request: StorageRequest):
        self.storage_request = storage_request

    def download(self, lpath: str) -> str:
        """Download artifact from storage"""
        # get path from registry
        registry = CardRegistry(self.storage_request.registry_type).list_cards(
            uid=self.storage_request.card_uid,
        )[0]

        uris = registry.get("uris")
        if uris is not None:
            path: str = uris.get(self.storage_request.uri_name)
            assert path is not None, f"URI {self.storage_request.uri_name} not found in registry"
            files = client.storage_client.list_files(path)

            if client.storage_client.backend == StorageSystem.LOCAL:
                return path

            return client.storage_client.download(
                rpath=path,
                lpath=lpath,
                recursive=False,
                **{"files": files},
            )
