# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from opsml.data.interfaces.custom_data.base import FileRecord, Metadata
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class TextRecord(FileRecord):
    """Text record to associate with text file

    Args:
        filepath:
            Full path to the file
        size:
            Size of the file. This is inferred automatically if filepath is provided.

    """

    def to_arrow(self, data_dir: Path, split_label: Optional[str] = None) -> Dict[str, Any]:
        """Saves data to arrow format

        Args:
            data_dir:
                Path to data directory
            split_label:
                Optional split label for data

        Returns:
            Dictionary of data to be saved to arrow
        """
        path = self.filepath.relative_to(data_dir)

        # write file
        with open(self.filepath, "rb") as file_:
            stream_record = {
                "split_label": split_label,
                "path": path.as_posix(),
                "bytes": file_.read(),
            }
        return stream_record


class TextMetadata(Metadata):
    """Create Image metadata from a list of ImageRecords

    Args:

        records:
            List of ImageRecords
    """

    records: List[TextRecord]

    @classmethod
    def load_from_file(cls, filepath: Path) -> "TextMetadata":
        """Load metadata from a file

        Args:
            filepath:
                Path to metadata file
        """
        assert filepath.name == "metadata.jsonl", "Filename must be metadata.jsonl"
        with filepath.open("r", encoding="utf-8") as file_:
            records = []
            for line in file_:
                records.append(TextRecord(**json.loads(line)))
            return cls(records=records)
