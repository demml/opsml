# Metadata

One of the benefits to the model registration process (especially when auto-converting to onnx) is the creation of model metadata that can be used in downstream application to load and run models via apis or batch jobs. The example below shows sample metadata that is produced with a registered model.


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
: Type of estimator (sklearn_estimator, sklearning_pipeline, pytorch, keras, etc.)

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