# FAQ

Below are a list of commonly answered questions.


### Why do some examples use a context manager and some don't? What's recommended?

By default, all cards can be registered, listed, loaded and updated outside of a context manager. In fact, this was done on purpose to not lock users into a particular style. The context manager comes into play when using `RunCards` as they provide a means to group artifacts (Cards, metrics, params) under a specific project run. Technically, this grouping can still be achieved by using `RunCards` directly but this comes at the expense of more lines of code. The context manager tends to be a more convenient way of logging and tracking artifacts. In addition, when using an `OpsmlProject`, all artifacts are automatically viewable in the Opsml UI.

Recommendation based on needs

- I'd like to be able to view all artifacts, metris, graphs, reports in a UI
    * Use the `OpsmlProject` context manager
- I don't really need to *see* all of the artifacts, I care more that they are tracked and callable when needed
    * Use whatever you prefer
- I like grouping runs/experiments by projects. UI doesn't really matter.
    * Use the `OpsmlProject` context manager

### How do I turn off onnx conversion?

Auto onnx conversion can be turned off by default. It can be turned on by setting `to_onnx=True` in the `ModelCard` constructor.

### How do I supply my own onnx definition?

If you'd like to create your onnx model yourself and associate that with the ModelCard, you will need to provide your own implementation of the `onnx_model` arg. An example of this can be seen [here](../interfaces/model/extras.md#onnxmodel).

### What's with using name, repository, and contact or `CardInfo` in the examples?

Every `ArtifactCard` requires a name, repository and user email. For convenience, you can instead provide a `CardInfo` instance.

### How is `Opsml` different than other products out there?

A key difference between `Opsml` and other products is that `Opsml` was not designed to be a platform or lock you in to any specific way of doing things. Instead, the goal and initial idea behind `Opsml` was to provide tooling and an interface that stitches, standardizes and automates some of the key building blocks (storage, tracking, versioning) to any machine learning workflow or platform. Thus, `Opsml` is capable of being used with other platforms or machine learning workflow systems. Or you can build your own!