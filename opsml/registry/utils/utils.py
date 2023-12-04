import importlib.util


def check_package_exists(package_name: str) -> bool:
    """Checks if package exists

    Args:
        package_name:
            Name of package to check

    Returns:
        True if package exists, False otherwise
    """
    return importlib.util.find_spec(package_name) is not None
