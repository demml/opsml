import sys
import tomli
import tomli_w


def update_package_name(toml_path, new_name):
    """Update the package name in pyproject.toml"""
    with open(toml_path, "rb") as f:
        data = tomli.load(f)

    data["project"]["name"] = new_name

    with open(toml_path, "wb") as f:
        tomli_w.dump(data, f)

    print(f"Package name updated to: {new_name}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: update_package_name.py <toml_path> <new_name>")
        sys.exit(1)

    update_package_name(sys.argv[1], sys.argv[2])
