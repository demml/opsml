from opsml import TextRecord, TextMetadata
from typing import Dict
from pathlib import Path
import json


class TextWriterHelper:
    def __init__(self):
        self.write_path = "examples/huggingface/data"

    def template(self, value: str, label: int) -> Dict[str, str]:
        return {"text": f"This is a sample {value} text record.", "label": label}

    def generate_text_records(self) -> Dict[str, str]:
        records = []
        for i in range(100):
            if i % 2 == 0:
                record = self.template(i, 1)
            else:
                record = self.template(i, 0)

            save_path = Path(f"{self.write_path}/text_{i}.txt")

            with open(save_path, "w") as f:
                f.write(json.dumps(record))

            records.append(TextRecord(filepath=save_path))

        metadata = TextMetadata(records=records)

        metadata.write_to_file(Path(f"{self.write_path}/metadata.jsonl"))
