# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from pathlib import Path
from typing import Dict, Optional, Union

import pyarrow as pa

from opsml.data.interfaces.custom_data.arrow_reader import PyarrowDatasetReader
from opsml.data.interfaces.custom_data.arrow_writer import PyarrowDatasetWriter
from opsml.data.interfaces.custom_data.base import (
    Dataset,
    check_for_dirs,
    get_metadata_filepath,
)
from opsml.data.interfaces.custom_data.text import TextMetadata
from opsml.helpers.logging import ArtifactLogger
from opsml.types import CommonKwargs

logger = ArtifactLogger.get_logger()


class TextDataset(Dataset):
    """Create a text dataset from a directory of files
    User can also provide a split that indicates the subdirectory of files to use.
    It is expected that each split contains a metadata.jsonl built from the TextMetadata class.
    TextDataset was built to have parity with HuggingFace.

    Args:
        data_dir:
            Root directory for text data.

            For example, the file is located at either:

                - "text/train/example.txt"
                - "text/example.txt"

            Then the data_dir should be `text/`

        shard_size:
            Size of shards to use for dataset. Default is 512MB.

        splits:
            Dictionary of splits to use for dataset. If no splits are provided, then the
            data_dir or subdirs will be used as the split. It is expected that each split contains a
            metadata.jsonl built from the TextMetadata class. It is recommended to allow opsml
            to create the splits for you.
    """

    splits: Dict[Optional[str], TextMetadata] = {}

    def save_data(self, path: Path) -> None:
        """Saves data to path. Base implementation use Joblib

        Args:
            path:
                Pathlib object
        """
        PyarrowDatasetWriter(self, path, self.arrow_schema).write_dataset_to_table()

    def load_data(self, path: Path, **kwargs: Union[str, int]) -> None:
        """Saves data to data_dir

        Args:
            path:
                Path to load_data

            kwargs:

                Keyword arguments to pass to the data loader

                ---- Supported kwargs for ImageDataset and TextDataset ----

                split:
                    Split to use for data. If not provided, then all data will be loaded.
                    Only used for subclasses of `Dataset`.

                batch_size:
                    What batch size to use when loading data. Only used for subclasses of `Dataset`.
                    Defaults to 1000.

                chunk_size:
                    How many files per batch to use when writing arrow back to local file.
                    Defaults to 1000.

                    Example:

                        - If batch_size=1000 and chunk_size=100, then the loaded batch will be split into
                        10 chunks to write in parallel. This is useful for large datasets.
        """
        PyarrowDatasetReader(dataset=self, lpath=path, **kwargs).load_dataset()  # type: ignore[arg-type]

    def split_data(self) -> None:
        """Creates data splits based on subdirectories of data_dir and supplied split value"""
        if bool(self.splits):
            return

        splits = check_for_dirs(self.data_dir)

        if bool(splits):
            for split in splits:
                self.splits[split] = TextMetadata.load_from_file(get_metadata_filepath(self.data_dir, split)[0])
        else:
            self.splits[None] = TextMetadata.load_from_file(get_metadata_filepath(self.data_dir)[0])

    @property
    def arrow_schema(self) -> pa.Schema:
        """Returns schema for TextData records

        Returns:
            pyarrow.Schema
        """

        return pa.schema(
            [
                pa.field("split_label", pa.string()),
                pa.field("path", pa.string()),
                pa.field("bytes", pa.binary()),
            ],
            metadata={
                "split_label": "label assigned to text",
                "path": "path to text",
                "bytes": "text bytes",
            },
        )

    @staticmethod
    def name() -> str:
        return TextDataset.__name__

    @property
    def data_type(self) -> str:
        return CommonKwargs.TEXT.value
