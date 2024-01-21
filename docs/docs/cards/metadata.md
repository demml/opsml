# Card Metadata

Both `ModelCard` and `ModelCardBatch` objects have a `metadata` attribute that can be used to store information about the model. If not provided, a default object is created. When registering a card, the metadata is updated with the latest information. In addition to automatically generated attributes, the `metadata` object can be used to store custom information about the model like descriptions.

### Optional User-Defined Attributes for both `ModelCardMetadata` and `DataCardMetadata

`description`: `Description`
: Description object for your model

### Description

Description is a simple data structure that can be used to store extra descriptive information about your model or data.

#### Args

`Summary`:  `Optional[str]`
: Summary text or pointer to a markdown file that describes the model or data

`Sample Code`: `Optional[str]`
: Sample code that can be used to load and run the model or data

`Notes`: `Optional[str]`
: Any additional information not captured by the other attributes


### Example
  
```python hl_lines="2 13"
from opsml import ModelCard, ModelCardMetadata
from opsml.types import Description, ModelCardMetadata

# logic for datacard or modelcard
...

modelcard = ModelCard(
  name="my_model",
  repository="my_repo",
  contact="user",
  interface=interface,
  datacard_uid=datacard.uid,
  metadata=ModelCardMetadata(description=Description(summary="my_summary.md")
  )
)
```

## Generate Model Metadata for Registered Models

One of the benefits to the model registration process (especially when auto-converting to onnx) is the creation of model metadata that can be used in downstream applications to load and run models via apis or batch jobs. The example below shows sample metadata that is produced with a registered model.


---
## Docs

::: opsml.types.Description
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

::: opsml.types.ModelCardMetadata
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3


::: opsml.types.DataCardMetadata
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Generate Model Metadata for Registered Models

One of the benefits to the model registration process (especially when auto-converting to onnx) is the creation of model metadata that can be used in downstream applications to load and run models via apis or batch jobs. The example below shows sample metadata that is produced with a registered model.


### **Example**

```json
{
  "model_name": "linear-reg",
  "model_type": "sklearn_estimator",
  "onnx_uri": "opsml/1/3d0112eca91e480dbf43a0f867566898/artifacts/MODEL/v-1.21.0/linear-reg-v1-21-0.onnx",
  "onnx_version": "1.14.0",
  "model_uri": "opsml/1/3d0112eca91e480dbf43a0f867566898/artifacts/MODEL/v-1.21.0/model.pkl",
  "model_version": "1.21.0",
  "sample_data": {
    "col_0": -4.963977338908213,
    "col_1": -6.2771861943273795,
    "col_2": -6.124374638979397,
    "col_3": -6.277861464467742,
    "col_4": -1.7837405438368172,
    "col_5": -4.901655711902971,
    "col_6": -4.680700041067267,
    "col_7": -1.431307102493668,
    "col_8": -4.504602023685907,
    "col_9": -1.6797834677244876
  },
  "data_schema": {
    "model_data_schema": {
      "data_type": "NUMPY_ARRAY",
      "input_features": {
        "inputs": {
          "feature_type": "FLOAT",
          "shape": [
            null,
            10
          ]
        }
      },
      "output_features": {
        "variable": {
          "feature_type": "FLOAT",
          "shape": [
            null,
            1
          ]
        }
      }
    },
    "input_data_schema": {
      "col_0": {
        "feature_type": "FLOAT",
        "shape": [
          null,
          1
        ]
      },
      "col_1": {
        "feature_type": "FLOAT",
        "shape": [
          null,
          1
        ]
      },
      "col_2": {
        "feature_type": "FLOAT",
        "shape": [
          null,
          1
        ]
      },
      "col_3": {
        "feature_type": "FLOAT",
        "shape": [
          null,
          1
        ]
      },
      "col_4": {
        "feature_type": "FLOAT",
        "shape": [
          null,
          1
        ]
      },
      "col_5": {
        "feature_type": "FLOAT",
        "shape": [
          null,
          1
        ]
      },
      "col_6": {
        "feature_type": "FLOAT",
        "shape": [
          null,
          1
        ]
      },
      "col_7": {
        "feature_type": "FLOAT",
        "shape": [
          null,
          1
        ]
      },
      "col_8": {
        "feature_type": "FLOAT",
        "shape": [
          null,
          1
        ]
      },
      "col_9": {
        "feature_type": "FLOAT",
        "shape": [
          null,
          1
        ]
      }
    }
  }
}
```

### **Args**

#### `model_name`
: Name of saved model

#### `model_type`
: Type of estimator (sklearn_estimator, sklearn_pipeline, pytorch, keras, etc.)

#### `onnx_uri`
: Storage location of onnx model

#### `onnx_version`
: Version of onnx package used to convert model

#### `model_uri`
: Storage location of original model

#### `model_version`
: Version associated with `ModelCard`

#### `sample_data`
: Sample data that can be used to test against trained or onnx model

#### `data_schema`
: Nested dictionary of data-related mappings

##### `model_data_schema`
: Onnx model data schema. `input_features` refers to what the onnx model expects. `output_features` refers to onnx model output

##### `input_data_schema`
: Input schema mapping of features and their types