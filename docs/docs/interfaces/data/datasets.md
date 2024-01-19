## Datasets

In addition to `DataInterface` classes, `opsml` also provides a `Dataset` class that is used when working with text or image data.


### Required Arguments for all Datasets (examples below)

`data_dir`
: Path to directory containing data. This should be the `root` directory that contains all of the data. If you wish to define **`splits`**, you can do so by creating sub-directories within the `root` directory. For example, if you have a `train` and `test` split, you can create a directory structure like this:

```
root
├── train        # this will be inferred as a split named `train`
│   ├── file1.txt
│   ├── file2.txt
│   ├── file3.txt
│   └── metadata.jsonl
└── test          # this will be inferred as a split named `test`
    ├── file4.txt
    ├── file5.txt
    ├── file6.txt
    └── metadata.jsonl
```

`shard_size`
: Size of each shard. Defaults to `512MB`

### Optional Arguments

`splits`
: Dictionary of splits. Defaults to `{}` This is automatically inferred from directory structure

`description`
: Description of dataset. Defaults to `Description()`


### Dataset Saving and Loading

Datasets are saved via `pyarrow` reader and writers. This allows for efficient loading and saving of datasets. For saving, `Dataset` splits are saved as parquet files based on the specified `shard` size. During loading, the dataset is loaded based on both `batch_size` and `chunk_size` arguments. The `batch_size` argument is used to specify the number of rows to load at a time. The `chunk_size` argument is used to split the batch by `n` chunks. Both of these arguments are used to control memory usage during loading.

### Metadata

The `metadata.jsonl` file is a `jsonl` file containing line separated json entries that can be written and loaded via the dataset's [`Metadata`](https://github.com/shipt/opsml/blob/3c84792ad81715c1a5ab66607d2398394f7492ba/opsml/data/interfaces/custom_data/base.py#L112) class. The `Metadata` class is a `pydantic` model that is used to validate the `metadata.jsonl` file. Each `metadata` subclass accepts a list of [`FileRecords`](https://github.com/shipt/opsml/blob/3c84792ad81715c1a5ab66607d2398394f7492ba/opsml/data/interfaces/custom_data/base.py#L58). For subclass-specific examples, please refer to the examples below.



## ImageDataset

[`ImageDataset`](https://github.com/shipt/opsml/blob/3c84792ad81715c1a5ab66607d2398394f7492ba/opsml/data/interfaces/_image.py#L24) is a subclass of `Dataset` that is used to load and save image data. It is similar to `HuggingFace` datasets, which was intentional in order to maintain some level of parity.

|  |  |
| --- | --- |
| **Data Type** | `Directory of images` |
| **Save Format** | [`parquet`](https://arrow.apache.org/docs/python/parquet.html) |
| **Source** | [`ImageDataset`](https://github.com/shipt/opsml/blob/main/opsml/data/interfaces/_image.py) |

---
### ImageMetadata

`ImageMetadata` is the metadata subclass that is associated with `ImageDataset`.

#### Required Arguments

`records`
: List of `ImageRecords`

::: opsml.ImageMetadata
    options:
        show_root_heading: true
        show_source: true
        heading_level: 4

---
### ImageRecord

`ImageRecord` is the `FileRecord` subclass that is associated with `ImageMetadata`.

#### Required Arguments

`filepath`
: Pathlike object to image file

#### Optional Arguments

`caption`
: Caption for the image

`categories`
: List of categories for the image

`objects`
: Bounding box specifications for objects in the image. See [`BBox`](https://github.com/shipt/opsml/blob/3c84792ad81715c1a5ab66607d2398394f7492ba/opsml/data/interfaces/custom_data/image.py#L17)


::: opsml.ImageRecord
    options:
        show_root_heading: true
        show_source: true
        heading_level: 4


### Example Writing Metadata

```python
# create images
from opsml import ImageRecord, ImageMetadata, BBox

records = []
record.append(ImageRecord(
        filepath=Path("image_dir/opsml.jpg"),
        caption="This is a caption for the image",
        categories=[0],
        objects=BBox(
            bbox=[[302.0, 109.0, 73.0, 52.0]],
            categories=[0]
        ),
    )
)

ImageMetadata(records=records).write_to_file(Path("image_dir/metadata.jsonl"))
```

### Example Using ImageDataset

```python hl_lines="1  6"
from opsml import ImageDataset, CardInfo, DataCard, CardRegistry

info = CardInfo(name="data", repository="opsml", contact="user@email.com")
data_registry = CardRegistry("data")

data = ImageDataset(path=Path("image_dir"))

# Create and register datacard
datacard = DataCard(interface=interface, info=info)
data_registry.register_card(card=datacard)
```


## TextDataset

[`TextDataset`](https://github.com/shipt/opsml/blob/3c84792ad81715c1a5ab66607d2398394f7492ba/opsml/data/interfaces/_text.py#L23) is a subclass of `Dataset` that is used to load and save test data. It is similar to `HuggingFace` datasets, which was intentional in order to maintain some level of parity.

|  |  |
| --- | --- |
| **Data Type** | `Directory of text files` |
| **Save Format** | [`parquet`](https://arrow.apache.org/docs/python/parquet.html) |
| **Source** | [`TextDataset`](https://github.com/shipt/opsml/blob/3c84792ad81715c1a5ab66607d2398394f7492ba/opsml/data/interfaces/_text.py#L23) |

---
### TextMetadata

`TextMetadata` is the metadata subclass that is associated with `TextDataset`.

#### Required Arguments

`records`
: List of `TextRecords`

::: opsml.TextMetadata
    options:
        show_root_heading: true
        show_source: true
        heading_level: 4

---
### TextRecord

`TextRecord` is the `FileRecord` subclass that is associated with `TextMetadata`.

#### Required Arguments

`filepath`
: Pathlike object to image file


::: opsml.TextRecord
    options:
        show_root_heading: true
        show_source: true
        heading_level: 4


### Example Writing Metadata

```python
from opsml import TextMetadata, TextRecord

record = TextRecord(filepath=Path("text_dir/opsml.txt"))

TextMetadata(records=[record]).write_to_file(Path("text_dir/metadata.jsonl"))
```

### Example Using TextDataset

```python hl_lines="1  6"
from opsml import TextDataset, CardInfo, DataCard, CardRegistry

info = CardInfo(name="data", repository="opsml", contact="user@email.com")
data_registry = CardRegistry("data")

data = TextDataset(path=Path("text_dir"))

# Create and register datacard
datacard = DataCard(interface=interface, info=info)
data_registry.register_card(card=datacard)
```
