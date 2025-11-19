import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent / "../python/opsml"


def copy_pyi_file(pyi_file: Path) -> None:
    """
    Copy a .pyi file to _{name}.pyi format.
    Special handling for __init__.pyi files - rename to parent folder name.

    Args:
        pyi_file: Path to the .pyi file to copy
    """
    if not pyi_file.exists():
        return

    # Determine the destination filename
    if pyi_file.name == "__init__.pyi":
        # For __init__.pyi, use parent folder name
        dest_name = f"_{pyi_file.parent.name}.pyi"
        dest_path = pyi_file.parent / dest_name
    else:
        # For regular .pyi files, prepend underscore
        dest_name = f"_{pyi_file.stem}.pyi"
        dest_path = pyi_file.parent / dest_name

    try:
        shutil.copyfile(pyi_file, dest_path)
        print(
            f"Copied {pyi_file.relative_to(BASE_DIR)} -> {dest_path.relative_to(BASE_DIR)}"
        )
    except Exception as e:
        print(f"Error copying {pyi_file}: {e}")


def process_directory(directory: Path) -> None:
    """
    Recursively process a directory and copy all .pyi files.

    Args:
        directory: Directory to process
    """
    if not directory.exists() or not directory.is_dir():
        print(f"Skipping non-existent directory: {directory}")
        return

    # Process all .pyi files in current directory
    for pyi_file in directory.glob("*.pyi"):
        copy_pyi_file(pyi_file)

    # Recursively process subdirectories
    for subdirectory in directory.iterdir():
        if subdirectory.is_dir() and not subdirectory.name.startswith("."):
            process_directory(subdirectory)


def main() -> None:
    """Main function to process all .pyi files in the opsml package."""
    print(f"Processing .pyi files in: {BASE_DIR.absolute()}")

    if not BASE_DIR.exists():
        print(f"Base directory does not exist: {BASE_DIR}")
        return

    process_directory(BASE_DIR)
    print("Processing complete!")


if __name__ == "__main__":
    main()
