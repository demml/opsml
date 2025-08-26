# type: ignore

import numpy as np
import tensorflow as tf
from opsml import (
    CardRegistry,
    ModelCard,
    ModelLoadKwargs,
    ModelSaveKwargs,
    RegistryType,
    TensorFlowModel,
)
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Concatenate, Dense

registry = CardRegistry(RegistryType.Model)


def multi_input_model():
    """Creates a multi-input model with numeric and categorical data."""
    num_samples = 100
    numeric_data = np.random.rand(num_samples, 10)
    categorical_data = np.random.randint(0, 5, size=(num_samples, 5))
    y = np.random.randint(0, 2, size=(num_samples, 1))

    # Define inputs
    numeric_input = Input(shape=(10,), name="numeric_input")
    categorical_input = Input(shape=(5,), name="categorical_input")

    # Process numeric branch
    numeric_branch = Dense(4, activation="relu", name="numeric_dense1")(numeric_input)
    numeric_branch = Dense(4, activation="relu", name="numeric_dense2")(numeric_branch)

    # Process categorical branch
    categorical_branch = Dense(4, activation="relu", name="categorical_dense1")(categorical_input)
    categorical_branch = Dense(4, activation="relu", name="categorical_dense2")(categorical_branch)

    # Combine branches
    combined = Concatenate(name="concat")([numeric_branch, categorical_branch])

    # Shared layers
    x = Dense(4, activation="relu", name="shared_dense")(combined)
    outputs = Dense(1, activation="sigmoid", name="output")(x)

    # Create model
    model = Model(
        inputs=[numeric_input, categorical_input],
        outputs=outputs,
        name="multi_input_model",
    )

    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    model.fit(
        [numeric_data, categorical_data],
        y,
        epochs=1,
        batch_size=32,
        validation_split=0.2,
        verbose=1,
    )

    input_signature = [
        tf.TensorSpec(shape=(None, 10), dtype=tf.float32, name="numeric_input"),
        tf.TensorSpec(shape=(None, 5), dtype=tf.float32, name="categorical_input"),
    ]
    save_kwargs = ModelSaveKwargs(
        onnx={"input_signature": input_signature},
        save_onnx=True,
    )

    return model, [numeric_data, categorical_data], save_kwargs


model, data, save_kwargs = multi_input_model()
interface = TensorFlowModel(model=model, sample_data=data)

modelcard = ModelCard(
    interface=interface,
    space="opsml",
    name="my_model",
)

# Register the model card
registry.register_card(
    modelcard,
    save_kwargs=save_kwargs,
)

# List the model card
modelcard_list = registry.list_cards(uid=modelcard.uid).as_table()


# Load the model card
loaded_modelcard: ModelCard = registry.load_card(modelcard.uid)

# Load the model card artifacts
loaded_modelcard.load(
    load_kwargs=ModelLoadKwargs(load_onnx=True),
)

assert loaded_modelcard.model is not None
assert loaded_modelcard.onnx_session is not None
