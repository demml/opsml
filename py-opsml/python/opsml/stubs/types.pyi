class VersionType:
    Major: "VersionType"
    Minor: "VersionType"
    Patch: "VersionType"
    Pre: "VersionType"
    Build: "VersionType"
    PreBuild: "VersionType"

    def __init__(self, version_type: str) -> None: ...
    def __eq__(self, other: object) -> bool: ...
