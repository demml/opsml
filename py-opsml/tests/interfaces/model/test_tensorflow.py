# type: ignore

import tensorflow as tf
import numpy as np
from opsml.model import TensorFlowModel, ModelSaveKwargs, ModelType, ModelLoadKwargs
from opsml.types import DataType
from tempfile import TemporaryDirectory
from pathlib import Path
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Dense, Concatenate
from opsml.logging import RustyLogger, LoggingConfig, LogLevel


# Sets up logging for tests
logger = RustyLogger.get_logger(LoggingConfig(log_level=LogLevel.Debug))


def build_model():
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Dense(10, activation="relu", input_shape=(10,)),
            tf.keras.layers.Dense(1),
        ]
    )
    # Compile
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    X = np.random.rand(100, 10)
    y = np.random.randint(0, 2, 100)

    # fit model
    model.fit(X, y, epochs=2)

    return model, X, None


def functional_model():
    # Define inputs
    inputs = Input(shape=(10,), name="input_layer")
    x = Dense(32, activation="relu", name="hidden_1")(inputs)
    x = Dense(16, activation="relu", name="hidden_2")(x)
    outputs = Dense(1, activation="sigmoid", name="output")(x)

    # Create model
    model = Model(inputs=inputs, outputs=outputs, name="functional_model")

    # Compile
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    X = np.random.rand(100, 10)
    y = np.random.randint(0, 2, 100)

    # fit model
    model.fit(X, y, epochs=1, batch_size=32, validation_split=0.2, verbose=1)

    input_signature = [tf.TensorSpec(shape=(None, 10), dtype=tf.float32, name="x")]
    save_kwargs = ModelSaveKwargs(
        onnx={"input_signature": input_signature}, save_onnx=True
    )

    return model, X, save_kwargs


def multi_input_model():
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
    categorical_branch = Dense(4, activation="relu", name="categorical_dense1")(
        categorical_input
    )
    categorical_branch = Dense(4, activation="relu", name="categorical_dense2")(
        categorical_branch
    )

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
        onnx={"input_signature": input_signature}, save_onnx=True
    )

    return model, [numeric_data, categorical_data], save_kwargs


def multi_input_dict_model():
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
    categorical_branch = Dense(4, activation="relu", name="categorical_dense1")(
        categorical_input
    )
    categorical_branch = Dense(4, activation="relu", name="categorical_dense2")(
        categorical_branch
    )

    # Combine branches
    combined = Concatenate(name="concat")([numeric_branch, categorical_branch])

    # Shared layers
    x = Dense(4, activation="relu", name="shared_dense")(combined)
    outputs = Dense(1, activation="sigmoid", name="output")(x)

    # Create model
    model = Model(
        inputs={"numeric_input": numeric_input, "categorical_input": categorical_input},
        outputs=outputs,
        name="multi_input_model",
    )

    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    train_data = {"numeric_input": numeric_data, "categorical_input": categorical_data}

    model.fit(
        train_data,
        y,
        epochs=1,
        batch_size=32,
        validation_split=0.2,
        verbose=1,
    )

    return model, train_data, None


def tf_test_model(tf_model, onnx: bool = False, data_type: DataType = DataType.Numpy):
    with TemporaryDirectory() as tmp_dir:
        temp_path = Path(tmp_dir)
        temp_path = temp_path / "test"

        temp_path.mkdir()

        model, data, save_kwargs = tf_model()

        interface = TensorFlowModel(model=model, sample_data=data)

        metadata = interface.save(temp_path, save_kwargs)
        assert metadata.version != "undefined"

        assert interface.model_type == ModelType.TensorFlow
        assert interface.data_type == data_type

        # list files
        interface.model = None
        assert interface.model is None

        if onnx:
            assert interface.onnx_session is not None
            interface.onnx_session.session = None
            assert interface.onnx_session.session is None

        interface.load(
            temp_path,
            metadata.save_metadata,
            ModelLoadKwargs(load_onnx=onnx),
        )

        assert interface.model is not None

        if onnx:
            assert interface.onnx_session is not None
            assert interface.onnx_session.session is not None


# pytest doesn't appear to work with tensorflow, so we are running our own script

if __name__ == "__main__":
    # testing functional model
    logger.debug("Testing functional model")
    tf_test_model(functional_model, True)

    # testing sequential model (doesn't work with onnx)
    logger.debug("Testing sequential model")
    tf_test_model(build_model, False)

    # testing multi input model
    logger.debug("Testing multi input model")
    tf_test_model(multi_input_model, True, DataType.List)

    # testing multi input dict model
    logger.debug("Testing multi input dict model")
    tf_test_model(multi_input_dict_model, False, DataType.Dict)
