from pathlib import Path
import os
from opsml.registry.storage.client import GCSFSStorageClient

# gcs integration tests perform operation on test bucket that has a TTL of 1 day for all objects
def test_gcsfs_integration(gcsfs_integration_client: GCSFSStorageClient, gcsfs_bucket: Path):
    lpath = Path("tests/assets/cats.jpg")
    rpath = gcsfs_bucket / "cats.jpg"
    
    # put file
    gcsfs_integration_client.put(lpath, rpath)
    
    # check file exists
    assert gcsfs_integration_client.exists(rpath)
    
    # list files
    files = gcsfs_integration_client.ls(gcsfs_bucket)
    assert len(files) == 1
    
    # find file
    assert gcsfs_integration_client.find(rpath) == [rpath.as_posix()]
    
    # get file
    get_lpath = Path("tests/assets/empty/cats.jpg")
    gcsfs_integration_client.get(rpath, get_lpath)
    assert get_lpath.exists()
    
    # remove local file
    os.remove(get_lpath.as_posix())
    
    # check iterfile
    for f in gcsfs_integration_client.iterfile(rpath, 1000):
        _bytes = lpath.read_bytes()
        
    # get mapper
    mapper = gcsfs_integration_client.get_mapper(gcsfs_bucket)
    assert mapper is not None
    
    # remove file
    gcsfs_integration_client.rm(rpath)
    
    # assert file is removed
    assert not gcsfs_integration_client.exists(rpath)
    
    
    