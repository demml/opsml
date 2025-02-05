import tensorflow as tf  # type: ignore
import numpy as np
from opsml.model import TensorFlowModel, SaveKwargs
from opsml.data import DataType
from tempfile import TemporaryDirectory
from pathlib import Path
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Dense
from opsml.core import RustyLogger, LoggingConfig, LogLevel


# Sets up logging for tests
RustyLogger.setup_logging(LoggingConfig(log_level=LogLevel.Debug))


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

    return model, X


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
    history = model.fit(X, y, epochs=1, batch_size=32, validation_split=0.2, verbose=1)

    return model, X


def test_functional_model():
    with TemporaryDirectory() as tmp_dir:
        temp_path = Path(tmp_dir)
        temp_path = temp_path / "test"

        temp_path.mkdir()

        model, data = functional_model()

        interface = TensorFlowModel(model=model, sample_data=data)

        assert interface.data_type == DataType.Numpy

        input_signature = [tf.TensorSpec(shape=(None, 10), dtype=tf.float32, name="x")]
        save_kwargs = SaveKwargs(onnx={"input_signature": input_signature})

        interface.save(temp_path, True, save_kwargs)

        # list files
        interface.model = None
        assert interface.model is None

        assert interface.onnx_session is not None
        interface.onnx_session.session = None

        assert interface.onnx_session.session is None

        interface.load(
            temp_path,
            model=True,
            onnx=True,
            sample_data=True,
        )

        assert interface.model is not None
        assert interface.onnx_session is not None
        assert interface.onnx_session.session is not None


# pytest doesn't appear to work with tensorflow, so we are running our own script

if __name__ == "__main__":
    test_functional_model()
