# Metadata


## Card Metadata

Both `ModelCard` and `DataCard` objects have a `metadata` attribute that can be used to store information about the model. If not provided, a default object is created. When registering a card, the metadata is updated with the latest information. In addition to automatically generated attributes, the `metadata` object can be used to store custom information about the model like descriptions.

### User-Defined Attributes (Optional)

`description`: `Description`
: Description object for your model

### Description

`Description` is a simple data structure that can be used to store extra descriptive information about your model or data.

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

---
### Docs

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

## Registered Model Metadata

One of the benefits to the model registration process (especially when auto-converting to onnx) is the creation of model metadata that can be used in downstream applications to load and run models via apis or batch jobs. The example below shows sample metadata that is produced with a registered model.


### **Example**

```json
{
    "model_name": "regression",
    "model_class": "SklearnEstimator",
    "model_type": "LinearRegression",
    "model_interface": "SklearnModel",
    "onnx_uri": "opsml-root:/OPSML_MODEL_REGISTRY/opsml/regression/v1.4.0/onnx-model.onnx",
    "onnx_version": "1.14.1",
    "model_uri": "opsml-root:/OPSML_MODEL_REGISTRY/opsml/regression/v1.4.0/trained-model.joblib",
    "model_version": "1.4.0",
    "model_repository": "opsml",
    "sample_data_uri": "opsml-root:/OPSML_MODEL_REGISTRY/opsml/regression/v1.4.0/sample-model-data.joblib",
    "opsml_version": "2.0.0",
    "data_schema": {
        "data_type": "numpy.ndarray",
        "input_features": {
            "inputs": {
                "feature_type": "float64",
                "shape": [
                    1,
                    10
                ]
            }
        },
        "output_features": {
            "outputs": {
                "feature_type": "float64",
                "shape": [
                    1,
                    1
                ]
            }
        },
        "onnx_input_features": {
            "predict": {
                "feature_type": "tensor(float)",
                "shape": [
                    null,
                    10
                ]
            }
        },
        "onnx_output_features": {
            "variable": {
                "feature_type": "tensor(float)",
                "shape": [
                    null,
                    1
                ]
            }
        },
        "onnx_data_type": null,
        "onnx_version": "1.14.1"
    }
}
```

::: opsml.ModelMetadata
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3