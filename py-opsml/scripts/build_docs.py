import os
import shutil

BASE_DIR = os.path.join(os.path.dirname(__file__), "../python/scouter")
FOLDERS = ["data", "experiment", "logging", "model", "potato_head", "scouter", "types"]
SCOUTER_SUBFOLDERS = ["alert", "client", "drift", "profile", "queue", "types"]


def copy_pyi(folder_path, name):
    src = os.path.join(folder_path, "__init__.pyi")
    dst = os.path.join(folder_path, f"_{name}.pyi")
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        print(f"Copied {src} -> {dst}")
    else:
        print(f"Skipped {name}: {src} does not exist")


def process_folder(folder, subfolders=None):
    folder_path = os.path.join(BASE_DIR, folder)
    if subfolders:
        for sub in subfolders:
            process_folder(os.path.join(folder, sub))
    else:
        name = os.path.basename(folder)
        copy_pyi(folder_path, name)


for folder in FOLDERS:
    if folder == "scouter":
        process_folder(folder, SCOUTER_SUBFOLDERS)
    else:
        process_folder(folder)
