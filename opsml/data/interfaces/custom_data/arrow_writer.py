import re
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

import pyarrow as pa
import pyarrow.parquet as pq

from opsml.data.interfaces.custom_data.base import Dataset, FileRecord
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class ShardSize(Enum):
    KB = 1e3
    MB = 1e6
    GB = 1e9


def yield_chunks(list_: List[FileRecord], size: int) -> Iterator[FileRecord]:
    """Yield successive n-sized chunks from list.

    Args:
        list_:
            list to chunk
        size:
            size of chunks

    """
    for _, i in enumerate(range(0, len(list_), size)):
        yield list_[i : i + size]


class PyarrowDatasetWriter:
    """Client side writer for pyarrow datasets"""

    def __init__(self, dataset: Dataset, write_path: Path, schema: pa.Schema):
        """Instantiates a PyarrowDatasetWriter object and writes dataset to pyarrow tables
        This class is used by all DataSet classes when saving to path. This class will ALWAYS
        write tables locally before uploading to server.

        Args:
            dataset:
                `Dataset` object
            write_path:
                Path to write dataset
        """

        self.dataset = dataset
        self.write_path = write_path
        self.shard_size = self._set_shard_size(dataset.shard_size)
        self.parquet_paths: List[str] = []
        self.schema = schema

    def _set_shard_size(self, shard_size: str) -> int:
        """
        Sets the shard size for the dataset. Defaults to 512MB if invalid shard size is provided

        Args:
            shard_size:
                `str` shard size in the format of <number><unit> e.g. 512MB, 1GB, 2KB

        Returns:
            int
        """
        shard_num_ = re.findall(r"\d+", shard_size)
        shard_size_ = re.findall(r"[a-zA-Z]+", shard_size)

        try:
            return int(int(shard_num_[0]) * ShardSize[shard_size_[0].upper()].value)

        except (IndexError, KeyError) as exc:
            logger.error("Invalid shard size: {}, error: {}", shard_size, exc)
            logger.info("Defaulting to 512MB")
            return int(512 * ShardSize.MB.value)

    def _create_record(self, record: Any) -> Dict[str, Any]:
        """Create record for pyarrow table

        Returns:
            Record dictionary and buffer size
        """
        raise NotImplementedError

    def _write_buffer(self, records: List[Dict[str, Any]], split_label: str) -> Path:
        try:
            temp_table = pa.Table.from_pylist(records, schema=self.schema)
            lpath = self.write_path / split_label / f"shard-{uuid.uuid4().hex}.parquet"

            pq.write_table(table=temp_table, where=lpath)

            return lpath

        except Exception as exc:
            logger.error("Exception occurred while writing to table: {}", exc)
            raise exc

    def create_path(self, sub_dir: str) -> None:
        """Create path to write files. If split name is defined, create split dir
        Args:
        split_label:
            `str` name of split
        """
        write_path = self.write_path / sub_dir
        write_path.mkdir(parents=True, exist_ok=True)

    def write_to_table(self, records: List[FileRecord], split_label: Optional[str] = None) -> str:
        """Write records to pyarrow table

        Args:
            records:
                `List[ImageRecord]`

            split_label:
                `str` name of split
        """

        processed_records = []
        for record in records:
            arrow_record = record.to_arrow(self.dataset.data_dir, split_label)
            processed_records.append(arrow_record)

        return self._write_buffer(processed_records, split_label)

    def write_dataset_to_table(self) -> List[str]:
        """Writes image dataset to pyarrow tables"""
        # get splits first (can be None, or more than one)
        # Splits are saved to their own paths for quick access in the future
        self.dataset.split_data()
        for split_label, metadata in self.dataset.splits.items():
            num_shards = int(max(1, metadata.size // self.shard_size))
            records_per_shard = len(metadata.records) // num_shards
            shard_chunks = list(yield_chunks(metadata.records, records_per_shard))

            # create subdir path
            if split_label:
                self.create_path(split_label)

            logger.info("Writing {} images to parquet for split {}", len(metadata.records), split_label)

            # don't want the overhead for one shard
            if num_shards == 1:
                for chunk in shard_chunks:
                    self.parquet_paths.append(self.write_to_table(chunk, split_label))

            else:
                with ProcessPoolExecutor() as executor:
                    future_to_table = {executor.submit(self.write_to_table, chunk, split_label): chunk for chunk in shard_chunks}
                    for future in as_completed(future_to_table):
                        try:
                            self.parquet_paths.append(future.result())
                        except Exception as exc:
                            logger.error("Exception occurred while writing to table: {}", exc)
                            raise exc

        return self.parquet_paths
