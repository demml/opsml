import re
from pathlib import Path

STUB_DIR = Path("python/opsml/stubs")
OUTPUT_FILE = Path("python/opsml/_opsml.pyi")

# Define stub files with their subdirectory structure
STUB_FILES = [
    "header.pyi",
    "common/logging.pyi",
    "agent/potato.pyi",
    "scouter/bifrost.pyi",
    "scouter/tracing.pyi",
    "scouter/evaluate.pyi",
    "scouter/mock.pyi",
    "scouter/scouter.pyi",
    "scouter/service_map.pyi",
    "service/agent.pyi",
    "types.pyi",
    "card.pyi",
    "opsml.pyi",
]


def strip_imports_section(content: str) -> str:
    """Remove the imports section between #### begin imports #### and #### end of imports ####"""
    pattern = r"####\s*begin\s+imports\s*####.*?####\s*end\s+of\s+imports\s*####\s*\n?"
    return re.sub(pattern, "", content, flags=re.DOTALL)


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

        # Strip imports section from all files except header.pyi
        if filename != "header.pyi":
            raw_text = strip_imports_section(raw_text)

        match = all_pattern.search(raw_text)
        if match:
            items = re.findall(r'"([^"]+)"|\'([^\']+)\'', match.group(1))
            master_all.extend(a or b for a, b in items)

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
