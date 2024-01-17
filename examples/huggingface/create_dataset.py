import json
from pathlib import Path
from typing import Dict

from opsml import TextMetadata, TextRecord


class TextWriterHelper:
    def __init__(self):
        self.write_path = Path("examples/huggingface/data")
        self.write_path.mkdir(parents=True, exist_ok=True)

    def template(self, value: str, label: int) -> Dict[str, str]:
        return {"text": f"This is a sample {value} text record.", "label": label}

    def generate_text_records(self) -> Dict[str, str]:
        records = []
        for i in range(100):
            if i % 2 == 0:
                record = self.template(i, 1)
            else:
                record = self.template(i, 0)

            save_path = self.write_path / f"text_{i}.txt"

            with open(save_path, "w") as f:
                f.write(json.dumps(record))

            records.append(TextRecord(filepath=save_path))

        metadata = TextMetadata(records=records)

        metadata.write_to_file(Path(self.write_path, "metadata.jsonl"))
