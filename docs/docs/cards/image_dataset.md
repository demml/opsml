# ImageDataset

In addition to `polars.DataFrame`, `pandas.DataFrame`, `numpy.ndarray` and `pyarrow.Table` you can also use the `ImageDataset` class to associate an image directory with a `DataCard`.

## Why?

In some cases you may want to associate a directory of images with a `DataCard`. This is useful for computer vision tasks where you may want to train a model on a directory of images, or load a directory  of images into something like a `Pytorch` or `HuggingFace` dataset.

## Usage

Assume we have the following directory structure:

```
├── my_images
    ├── file1.jpg
    ├── file2.jpg
    └── metadata.jsonl
```

`my_images` contains two images and a metadata file. We can use the `ImageDataset` class to associate this directory with a `DataCard`. **Note** you can configure all file contents under `my_images` as you see fit (additional directories, etc.). The only requirement is that the `metadata.jsonl` file exists under the top-level directory (in this case `my_images`).

This structure is similar to `HuggingFace` datasets, which was intentional in order to maintain some level of parity.

### Metadata anatomy

The `metadata.jsonl` file is a `jsonl` file containing line separated json entries that follow the following specification:

`file_name`
: Name of the file (Required)

`caption`
: Caption for the image (Optional)

`categories`
: List of categories for the image (Optional)

`objects`
: Bounding box specifications for objects in the image (Optional)

#### Bounding Box Specification

`bbox`
: List of bounding box coordinates (Required)

`categories`
: List of categories for the bounding box (Required)

**Example metadata records**

```json
{"file_name": "0001.png", "objects": {"bbox": [[302.0, 109.0, 73.0, 52.0]], "categories": [0]}}
{"file_name": "0002.png", "caption": "This is a second value of a text feature you added to your images"}
{"file_name": "0002.png", "objects": {"bbox": [[810.0, 100.0, 57.0, 28.0]], "categories": [1]}}
{"file_name": "0003.png", "objects": {"bbox": [[160.0, 31.0, 248.0, 616.0], [741.0, 68.0, 202.0, 401.0]], "categories": [2, 2]}}
```

#### Building with python

If you'd like to build the `metadata.jsonl` file with python, you can use the `ImageMetadata` and `ImageRecord` classes.

```python
from opsml.registry import DataCard
from opsml.registry.image import ImageDataset, ImageMetadata, ImageRecord, BBox

# Create one metadata record
record = ImageRecord(
    file_name="0001.png",
    caption="This is a caption for the image",
    categories=[0],
    objects=BBox(
        bbox=[[302.0, 109.0, 73.0, 52.0]],
        categories=[0]
    ),
)

metadata = ImageMetadata(records=[record])

# if you'd like to write the metadata to file
metadata.write_to_file("my_images/metadata.jsonl")

# Create image dataset
image_dataset = ImageDataset(
    image_dir="my_images",
    metadata=metadata # or if you wrote the file to disk, metadata="metadata.jsonl"
)


# Create DataCard
DataCard(
    data = image_dataset,
    **kwargs
)

```

## Docs

::: opsml.registry.image.dataset
    options:
        members:
            - ImageDataset
            - ImageMetadata
            - ImageRecord
            - BBox
        show_root_heading: true
        show_source: true
        heading_level: 3

