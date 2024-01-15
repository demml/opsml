# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from pathlib import Path, Dict
import pyarrow as pa
from opsml.data.interfaces.custom_data.base import (
    Dataset,
    check_for_dirs,
    get_metadata_filepath,
)
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

try:
    from opsml.data.interfaces.custom_data.image import ImageMetadata

    class ImageData(Dataset):

        """Create an image dataset from a directory of images.
        User can also provide a split that indicates the subdirectory of images to use.
        It is expected that each split contains a metadata.jsonl built from the ImageMetadata class.
        ImageData was built to have parity with HuggingFace.

        Args:
            data_dir:
                Root directory for images.

                For example, you the image file is located at either:
                - `images/train/my_image.png`
                - `images/my_image.png`
                Then the data_dir should be `images/`
            shard_size:
                Size of shards to use for dataset. Default is 512MB.
            batch_size:
                Batch size for dataset. Default is 1000.
            splits:
                Dictionary of splits to use for dataset. If no splits are provided, then the
                data_dir or subdirs will be used as the split. It is expected that each split contains a
                metadata.jsonl built from the ImageMetadata class. It is recommended to allow opsml
                to create the splits for you.
        """

        splits: Dict[str, ImageMetadata] = {}

        def save_data(self, path: Path) -> None:
            """Saves data to path. Base implementation use Joblib

            Args:
                path:
                    Pathlib object
            """

        def split_data(self) -> None:
            """Creates data splits based on subdirectories of data_dir and supplied split value

            Returns:
                None
            """
            if bool(self.splits):
                return

            splits = check_for_dirs(self.data_dir)

            if bool(splits):
                for split in splits:
                    self.splits[split] = ImageMetadata.load_from_file(
                        get_metadata_filepath(self.data_dir, split),
                    )
            else:
                self.splits[None] = ImageMetadata.load_from_file(
                    get_metadata_filepath(self.data_dir, split),
                )

        @property
        def arrow_schema(self) -> pa.Schema:
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

except ModuleNotFoundError:
    pass
