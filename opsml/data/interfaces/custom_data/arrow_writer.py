import re
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Iterator, Union

import pyarrow as pa
import pyarrow.parquet as pq
from fsspec.implementations.local import LocalFileSystem
from pydantic import BaseModel, ConfigDict, field_validator

from opsml.helpers.logging import ArtifactLogger

# from opsml.regis import ImageDataset, ImageRecord
from opsml.data.interfaces.custom_data.base import Dataset

# try to import pillow for ImageDataset dependency
try:
    from PIL import Image
except ImportError:
    pass


logger = ArtifactLogger.get_logger()


class ShardSize(Enum):
    KB = 1e3
    MB = 1e6
    GB = 1e9


def yield_chunks(list_: List[Any], size: int) -> Iterator[Any]:
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

    def __init__(self, dataset: Dataset):
        """Instantiates a PyarrowDatasetWriter object

        Args:
            info:
                DatasetWriteInfo object
        """

        self.dataset = dataset
        self.shard_size = self._set_shard_size(dataset.shard_size)
        self.parquet_paths: List[str] = []

    @property
    def schema(self) -> pa.Schema:
        raise NotImplementedError

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

    def _write_buffer(self, records: List[Dict[str, Any]], split_name: str) -> str:
        try:
            temp_table = pa.Table.from_pylist(records, schema=self.schema)
            write_path = self.info.write_path / split_name / f"shard-{uuid.uuid4().hex}.parquet"

            pq.write_table(
                table=temp_table,
                where=write_path,
                filesystem=self.info.storage_filesystem,
            )

            return str(write_path)

        except Exception as exc:
            logger.error("Exception occurred while writing to table: {}", exc)
            raise exc

    def create_path(self, split_name: str) -> None:
        """Create path to write files. If split name is defined, create split dir
        Args:
        split_name:
            `str` name of split
        """
        write_path = str(self.info.write_path / split_name)
        self.info.storage_filesystem.create_dir(write_path)

    def write_to_table(self, records: List[Any], split_name: str) -> str:
        """Write records to pyarrow table

        Args:
            records:
                `List[ImageRecord]`

            split_name:
                `str` name of split
        """

        processed_records = []
        for record in records:
            arrow_record = self._create_record(record)
            processed_records.append(arrow_record)

        return self._write_buffer(processed_records, split_name)

    def write_dataset_to_table(self) -> List[str]:
        """Writes image dataset to pyarrow tables"""
        # get splits first (can be None, or more than one)
        # Splits are saved to their own paths for quick access in the future
        splits = self.dataset.split_data()
        for name, split in splits:
            num_shards = int(max(1, split.size // self.shard_size))
            records_per_shard = len(split.records) // num_shards
            shard_chunks = list(yield_chunks(split.records, records_per_shard))

            # create split name path
            self.create_path(name)

            logger.info("Writing {} images to parquet for split {}", len(split.records), name)

            # don't want the overhead for one shard
            if num_shards == 1:
                for chunk in shard_chunks:
                    self.parquet_paths.append(self.write_to_table(chunk, name))

            else:
                with ProcessPoolExecutor() as executor:
                    future_to_table = {executor.submit(self.write_to_table, chunk, name): chunk for chunk in shard_chunks}
                    for future in as_completed(future_to_table):
                        try:
                            self.parquet_paths.append(future.result())
                        except Exception as exc:
                            logger.error("Exception occurred while writing to table: {}", exc)
                            raise exc

        return self.parquet_paths


# this can be extended to language datasets in the future
class ImageDatasetWriter(PyarrowDatasetWriter):
    @property
    def schema(self) -> pa.Schema:
        """Returns schema for ImageDataset records"""

        return pa.schema(
            [
                pa.field("split_label", pa.string()),
                pa.field("path", pa.string()),
                pa.field("height", pa.int32()),
                pa.field("width", pa.int32()),
                pa.field("bytes", pa.binary()),
                pa.field("mode", pa.string()),
            ],
            metadata={
                "splt_label": "label assigned to image",
                "path": "path to image",
                "mode": "image mode",
                "height": "image height",
                "width": "image width",
                "bytes": "image bytes",
            },
        )

    def _create_record(self, record: ImageRecord) -> Dict[str, Any]:
        """Create record for pyarrow table

        Returns:
            Record dictionary and buffer size
        """

        image_path = str(Path(f"{record.path}/{record.filename}"))

        with Image.open(image_path) as img:
            stream_record = {
                "split_label": record.split,
                "path": str(Path(record.split or "") / record.filename),
                "height": img.height,
                "width": img.width,
                "bytes": img.tobytes(),
                "mode": img.mode,
            }

        return stream_record
