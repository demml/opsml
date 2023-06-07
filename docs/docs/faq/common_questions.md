# FAQ

Below are a list of commonly answered questions.


### Why do some examples use a context manager and some don't? What's recommended?

By default, all cards can be registered, listed, loaded and updated outside of a context manager. In fact, this was done on purpose to not lock users into a particular style. The context manager comes into play when using `RunCards` as they provide a means to group artifacts (Cards, metrics, params) under a specific project run. Technically, this grouping can still be achieved by using `RunCards` directly but this comes at the expense of more lines of code. The context manager tends to be a more convenient ways to log and track artifacts. In addition, when using a `MlflowProject`, all artifacts are automatically viewable in the Mlflow UI.

Recommendation based on needs

- I'd like to be able to view all artifacts, metris, graphs, reports in a UI 
    * Use the `MlflowProject` context manager
- I don't really need to *see* all of the artifacts, I care more that they are tracked and callable when needed 
    * Use whatever you prefer
- I like grouping runs/experiments by projects. UI doesn't really matter.
    * Use the `MlflowProject` or `OpsmlProject` context managers
- My server is setup to use Mlflow as a UI.
    * Use `MlflowProject` context manager

### How do I turn off onnx conversion?

Auto onnx conversion can be turned off via the `to_onnx` arg when creating a ModelCard. `False` = no onnx conversion.

### How do I supply my own onnx definition?

If you'd like to create your onnx model yourself and associate that with the ModelCard, you will need to provide your own implementation of the `onnx_model_def` arg. An example of this can be seen [here](../cards/onnx.md).

### What's with using name, team, and user_email or `CardInfo` in the examples?

Every `ArtifactCard` requires a name, team and user email. For convenience, you can instead provide a `CardInfo` instance instead.