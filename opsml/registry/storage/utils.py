import shutil
from functools import wraps
from typing import Any, Callable


def cleanup_files(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for deleting files if needed"""

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:  # type: ignore[no-untyped-def]
        artifact, loadable_filepath = func(self, *args, **kwargs)

        if isinstance(loadable_filepath, list):
            loadable_filepath = loadable_filepath[0]

        if isinstance(loadable_filepath, str):
            if "temp" in loadable_filepath:  # make this better later
                file_dir = "/".join(loadable_filepath.split("/")[:-1])
                shutil.rmtree(file_dir, ignore_errors=True)
        return artifact

    return wrapper
