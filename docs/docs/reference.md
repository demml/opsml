The following is a small list of frequently used classes and methods in `OpsML`. Refer to specific documentation and/or api specs for detailed information.


## All Cards

### Registering a card

```python

from opsml import CardRegistries, ModelCard

registries = CardRegistries()

card = ModelCard(name={name}, repository={repository}, version={version})
registries.model.register_card(card)

# This also works

from opsml import CardRegistry

registry = CardRegistry("model")
registry.register_card(card)
```

### Loading a card

```python

registry.load_card(name={name}, repository={repository}, version={version})

# or 

registry.load_card(uid={uid})

# or

from opsml import CardInfo
info = CardInfo(name={name}, repository={repository}, version={version})
registry.load_card(info=info)
```

## ModelCards

### Loading a model

```python

modelcard = registry.load_card(name={name}, repository={repository}, version={version})
modelcard.load_model()

# with preprocessor
modelcard.load_model(load_preprocessor=True)

# access model
modelcard.model
```

### Loading an onnx model

```python

modelcard = registry.load_card(name={name}, repository={repository}, version={version})
modelcard.load_onnx_model()

# with preprocessor
modelcard.load_onnx_model(load_preprocessor=True)

# access model
modelcard.onnx_model
```

### Downloading a model to file

```python

modelcard.download_model(path={path}, load_preprocessor=True)

# download onnx model
modelcard.download_model(path={path}, load_onnx=True)

# download quantized onnx model (huggingface only)
modelcard.download_model(path={path}, load_onnx=True, quantized=True)

# load model from ModelLoader
loader = ModelLoader(path={path})
loader.load_model()
loader.model

# load onnx version from loader
loader = ModelLoader(path={path})
loader.load_onnx_model()
loader.onnx_model
```
 