from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

import pyarrow.dataset as ds

from opsml.data.interfaces.custom_data.base import (
    Dataset,
    get_metadata_filepath,
    yield_chunks,
)
from opsml.helpers.logging import ArtifactLogger
from opsml.storage import client

logger = ArtifactLogger.get_logger()
local_fs = client.LocalFileSystem(auto_mkdir=True)


class PyarrowDatasetReader:
    def __init__(
        self,
        dataset: Dataset,
        lpath: Path,
        batch_size: int = 1000,
        chunk_size: int = 1000,
        split: Optional[str] = None,
        **kwargs: Union[str, int],
    ):
        """Instantiates a PyarrowReaderBase and reads dataset from pyarrow tables

        Args:
            dataset:
                `Dataset` object
            lpath:
                Path to read dataset from
            batch_size:
                Batch size to use for loading dataset
            split:
                Optional split to use for the dataset. If not provided, all images in the data_dir will be used.
                If provided, lpath will be checked if it already contains the split label. If not, the split label
                will be appended to the path.
        """
        self.dataset = dataset
        self.lpath = lpath
        self.batch_size = batch_size
        self.split = split
        self.chunk_size = chunk_size

        if self.split is not None:
            # check if split in lpath
            if self.split not in self.lpath.parts:
                self.lpath = self.lpath / self.split

    @property
    def arrow_dataset(self) -> ds.Dataset:
        """Returns a pyarrow dataset"""
        return ds.dataset(source=self.lpath, format="parquet", ignore_prefixes=["metadata.jsonl"])

    def _write_data_to_file(self, files: List[Dict[str, Any]]) -> None:
        """Writes a list of pyarrow data to image files.

        Args:
            files:
                List of tuples containing filename, image_bytes, and split_label
        """

        for record in files:
            write_path = Path(self.dataset.data_dir, cast(str, record["path"]))
            try:
                with write_path.open("wb") as file_:
                    file_.write(record["bytes"])

            except Exception as exc:
                logger.error("Exception occurred while writing to file: {}", exc)
                raise exc

    def _write_batch_to_file(self, arrow_batch: List[Dict[str, Any]]) -> None:
        """Write arrow data to file

        Args:
            arrow_batch:
                List of pyarrow file data
        """

        # get chunks
        chunks = list(yield_chunks(arrow_batch, self.chunk_size))

        # don't want overhead of instantiating a process pool if we don't need to
        if len(chunks) == 1:
            self._write_data_to_file(chunks[0])

        else:
            with ProcessPoolExecutor() as executor:
                future_to_table = {executor.submit(self._write_data_to_file, chunk): chunk for chunk in chunks}
                for future in as_completed(future_to_table):
                    try:
                        _ = future.result()
                    except Exception as exc:
                        logger.error("Exception occurred while writing to file: {}", exc)
                        raise exc

    def load_dataset(self) -> None:
        """Loads a pyarrow dataset and writes to file"""

        # Get metadata first
        paths = get_metadata_filepath(self.lpath)

        # move metadata files from lpath to dataset.data_dir
        for lpath in paths:
            if self.split is not None:
                # split will be the last directory in path
                rpath = self.dataset.data_dir / lpath.relative_to(self.lpath.parent)

            else:
                # split label will not be in path
                rpath = self.dataset.data_dir / lpath.relative_to(self.lpath)

            # this will always be local fs
            local_fs.put(str(lpath), str(rpath))
            local_fs.rm(str(lpath))

        for record_batch in self.arrow_dataset.to_batches(batch_size=self.batch_size):
            self._write_batch_to_file(record_batch.to_pylist())
