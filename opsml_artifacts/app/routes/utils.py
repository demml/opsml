import shutil


def delete_dir(dir_path: str):
    """Deletes a file"""

    try:
        shutil.rmtree(dir_path)
    except Exception as error:
        raise ValueError(f"Failed to delete {file_path}. {error}")
