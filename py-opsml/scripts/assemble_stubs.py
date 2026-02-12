import re
from pathlib import Path

STUB_DIR = Path("python/opsml/stubs")
OUTPUT_FILE = Path("python/opsml/_opsml.pyi")

# Define stub files with their subdirectory structure
STUB_FILES = [
    "header.pyi",
    "common/logging.pyi",
    "genai/potato.pyi",
    "scouter/tracing.pyi",
    "scouter/evaluate.pyi",
    "scouter/mock.pyi",
    "scouter/scouter.pyi",
    "opsml.pyi",
]


def strip_imports_section(content: str) -> str:
    """Remove the imports section between #### begin imports #### and #### end of imports ####"""
    pattern = r"####\s*begin\s+imports\s*####.*?####\s*end\s+of\s+imports\s*####\s*\n?"
    return re.sub(pattern, "", content, flags=re.DOTALL)


def assemble():
    final_content = [
        "# AUTO-GENERATED STUB FILE. DO NOT EDIT.",
        "# pylint: disable=redefined-builtin, invalid-name, dangerous-default-value, missing-final-newline, arguments-differ",
    ]
    master_all = []

    all_pattern = re.compile(r"__all__\s*=\s*\[(.*?)\]", re.DOTALL)

    for filename in STUB_FILES:
        file_path = STUB_DIR / filename
        if not file_path.exists():
            print(f"Warning: {file_path} not found, skipping...")
            continue

        raw_text = file_path.read_text(encoding="utf-8")

        # Strip imports section from all files except header.pyi
        if filename != "header.pyi":
            raw_text = strip_imports_section(raw_text)

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

        # Use the relative path as the section marker for clarity
        final_content.append(f"### {filename} ###")
        final_content.append(text_to_append.strip())
        final_content.append("\n")

    final_content.append("### GLOBAL EXPORTS ###")
    final_content.append("__all__ = [")
    for item in sorted(set(master_all)):
        final_content.append(f'    "{item}",')
    final_content.append("]")

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        f.write("\n".join(final_content))

    print(f"✓ Compiled {len(set(master_all))} unique exports into {OUTPUT_FILE}")
    print(f"  Processed {len(STUB_FILES)} stub files:")
    for stub in STUB_FILES:
        status = "✓" if (STUB_DIR / stub).exists() else "✗"
        print(f"    {status} {stub}")


if __name__ == "__main__":
    assemble()
