import shutil


def delete_dir(dir_path: str):
    """Deletes a file"""

    try:
        shutil.rmtree(dir_path)
    except Exception as error:  # pylint: disable=broad-except
        raise ValueError(f"Failed to delete {dir_path}. {error}") from error
