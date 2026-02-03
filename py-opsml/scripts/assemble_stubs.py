import re
from pathlib import Path

STUB_DIR = Path("python/opsml/stubs")
OUTPUT_FILE = Path("python/opsml/_opsml.pyi")

# Order matters here. dont change
STUB_FILES = [
    "header.pyi",
    "logging.pyi",
    "potato.pyi",
    "scouter.pyi",
    "opsml.pyi",
]


def assemble():
    final_content = [
        "# AUTO-GENERATED STUB FILE. DO NOT EDIT.",
        "# pylint: disable=redefined-builtin, invalid-name, dangerous-default-value",
    ]
    master_all = []

    all_pattern = re.compile(r"__all__\s*=\s*\[(.*?)\]", re.DOTALL)

    for filename in STUB_FILES:
        file_path = STUB_DIR / filename
        if not file_path.exists():
            continue

        raw_text = file_path.read_text(encoding="utf-8")

        match = all_pattern.search(raw_text)
        if match:
            items = [
                i.strip().replace('"', "").replace("'", "")
                for i in match.group(1).split(",")
                if i.strip()
            ]
            master_all.extend(items)

            text_to_append = all_pattern.sub("", raw_text)
        else:
            text_to_append = raw_text

        final_content.append(f"### {filename} ###")
        final_content.append(text_to_append.strip())
        final_content.append("\n")

    final_content.append("### GLOBAL EXPORTS ###")
    final_content.append("__all__ = [")
    for item in sorted(list(set(master_all))):
        final_content.append(f'    "{item}",')
    final_content.append("]")

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        f.write("\n".join(final_content))
    print(f"Compiled {len(master_all)} exports into {OUTPUT_FILE}")


if __name__ == "__main__":
    assemble()
