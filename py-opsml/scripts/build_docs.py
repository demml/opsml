import os
import shutil

BASE_DIR = os.path.join(os.path.dirname(__file__), "../python/opsml")
FOLDERS = [
    "card",
    "data",
    "experiment",
    "logging",
    "model",
    "llm",
    "scouter",
    "types",
    "mock",
    "app",
    "evaluate",
]
SCOUTER_SUBFOLDERS = ["alert", "client", "drift", "profile", "queue", "types"]
LLM_SUBFOLDERS = ["google", "openai"]


def copy_pyi(folder_path, name):
    src = os.path.join(folder_path, "__init__.pyi")
    dst = os.path.join(folder_path, f"_{name}.pyi")
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        print(f"Copied {src} -> {dst}")
    else:
        print(f"Skipped {name}: {src} does not exist")


def process_folder(folder):
    folder_path = os.path.join(BASE_DIR, folder)
    copy_pyi(folder_path, os.path.basename(folder))


for folder in FOLDERS:
    if folder == "scouter":
        for subfolder in SCOUTER_SUBFOLDERS:
            process_folder(os.path.join(folder, subfolder))
    elif folder == "llm":
        for subfolder in LLM_SUBFOLDERS:
            process_folder(os.path.join(folder, subfolder))
        # process main folder for llm
        process_folder(folder)
    else:
        process_folder(folder)
