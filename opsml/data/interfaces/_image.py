# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from pathlib import Path
from typing import Dict, List, Optional


from opsml.data.interfaces.custom_data.base import Dataset
from opsml.data.interfaces.custom_data.image import ImageMetadata
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


def check_for_dirs(data_dir: Path) -> List[str]:
    """Checks if data_dir contains subdirectories and returns a list of subdirectories

    Args:
        data_dir:
            Path to data directory

    Returns:
        List of subdirectories
    """
    dirs = [x.as_posix() for x in data_dir.iterdir() if x.is_dir()]
    return dirs


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

    def _load_metadata_from_file(self, data_dir: Path, split: Optional[str]) -> ImageMetadata:
        """Loads metadata file from data_dir or subdirectory of data_dir

        Args:
            data_dir:
                Path to data directory
            split:
                Optional split to use for the dataset. If not provided, all images in the data_dir will be used.

        Returns:
            `ImageMetadata`
        """
        search_path = data_dir

        if split is not None:
            search_path = data_dir / split

        for p in search_path.rglob("*.jsonl"):
            if p.name == "metadata.jsonl":
                return ImageMetadata.from_file(p)

        raise ValueError(f"Could not find metadata.jsonl in {data_dir} or subdirectories")
