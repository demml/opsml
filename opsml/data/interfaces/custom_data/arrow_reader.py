from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, cast

import pyarrow.dataset as ds

from opsml.data.interfaces.custom_data.base import Dataset, yield_chunks
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class PyarrowDatasetReader:
    def __init__(self, dataset: Dataset, lpath: Path, batch_size: int = 1000):
        """Instantiates a PyarrowReaderBase and reads dataset from pyarrow tables

        Args:
            dataset:
                `Dataset` object
            lpath:
                Path to read dataset from
            batch_size:
                Batch size to use for loading dataset
        """
        self.dataset = dataset
        self.lpath = lpath
        self.batch_size = batch_size

    @property
    def arrow_dataset(self) -> ds.Dataset:
        """Returns a pyarrow dataset"""
        return ds.dataset(source=self.lpath, format="parquet")

    def _write_data_to_file(self, files: List[Dict[str, Any]]) -> None:
        """Writes a list of pyarrow data to image files.

        Args:
            files:
                List of tuples containing filename, image_bytes, and split_label
        """

        for record in files:
            write_path = Path(self.dataset.data_dir, cast(str, record["path"]))
            write_path.mkdir(parents=True, exist_ok=True)

            try:
                with write_path.open("wb") as file_:
                    file_.write(record["bytes"])  # type: ignore

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
        chunks = list(yield_chunks(arrow_batch, 100))

        # don't want overhead of instantiating a process pool if we don't need to
        if len(chunks) == 1:
            self._write_data_to_file(chunks[0])

        else:
            with ProcessPoolExecutor() as executor:
                future_to_table = {executor.submit(self._write_data_to_images, chunk): chunk for chunk in chunks}
                for future in as_completed(future_to_table):
                    try:
                        _ = future.result()
                    except Exception as exc:
                        logger.error("Exception occurred while writing to file: {}", exc)
                        raise exc

    def load_dataset(self) -> None:
        """Loads a pyarrow dataset and writes to file"""
        self.check_write_paths_exist()

        for record_batch in self.arrow_dataset.to_batches(batch_size=self.batch_size):
            self.write_batch_to_file(record_batch.to_pylist())
