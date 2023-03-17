from typing import Protocol


class Info(Protocol):
    _artifact_uri: str


class ActiveRun(Protocol):
    info: Info
