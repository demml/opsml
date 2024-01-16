## Metaflow Examples
<img width="640px" src="../../images/metaflow-logo.png" alt="metaflow" class="center" href="https://metaflow.org/" />

The following examples demonstrate how to use Opsml with a simple Metaflow pipeline.

### flow

Includes examples of:

- Creating a 3 step `FlowSpec`
- 1st step creates a `DataCard` with a pandas dataframe
- 2nd step creates a `ModelCard` with a linear regressor and auto-onnx conversion
- 3rd step loads data and model cards and test's onnx model
