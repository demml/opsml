from typing import Any
from opsml.registry.types import StorageRequest
from opsml.registry.storage import client


class Downloader:
    def __init__(self, storage_request: StorageRequest):
        self.storage_request = storage_request

    def download(self) -> Any:
        """Download artifact from storage"""
        raise NotImplementedError


class APIDownloader:
    def __init__(self, storage_request: StorageRequest):
        self.storage_request = storage_request

    def download(self, rpath: str) -> Any:
        """Download artifact from storage"""
        return client.storage_client.download(self.storage_request)
