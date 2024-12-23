import os

# Unset the environment variables
os.environ.pop("GOOGLE_ACCOUNT_JSON_BASE64", None)
os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS_JSON", None)
os.environ["OPSML_TRACKING_URI"] = "http://localhost:3000"


if __name__ == "__main__":
    from pathlib import Path
    import os
    import uuid

    from opsml_core import PyFileSystemStorage, OpsmlConfig

    config = OpsmlConfig(client_mode=True)

    storage_client = PyFileSystemStorage(config.storage_settings())
    print(storage_client.name())
    print(storage_client.storage_type())
    # print("client loaded")

    # path = Path("inkscape")

    # files = storage_client.find(path)

    # info = storage_client.find_info(path)

    lpath = Path("tests/assets")
    rpath_dir = Path(uuid.uuid4().hex)
    rpath = rpath_dir / "assets"

    storage_client.put(lpath, rpath, recursive=True)
    storage_client.rm(rpath, recursive=True)

    # kwargs = {
    #    "base_url": "http://localhost:3000",
    #    "path_prefix": "opsml",
    # }
    # storage_uri = "http://localhost:3000"
    # storage_type = StorageType.Google
    # settings = StorageSettings(storage_uri, True, storage_type, kwargs)
#
# client = PyHttpFSStorageClient(settings)
#
# lpath = Path("tests/assets/cats.jpg")
# rpath_dir = Path(uuid.uuid4().hex)
# rpath = rpath_dir / "cats.jpg"
#
# client.put(lpath, rpath)
