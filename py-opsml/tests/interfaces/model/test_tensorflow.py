import tensorflow as tf  # type: ignore
import numpy as np
from opsml.model import TensorFlowModel
from opsml.data import DataType
from tempfile import TemporaryDirectory
from pathlib import Path

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


# pytest doesn't appear to work with tensorflow, so we are running our own script

if __name__ == "__main__":
    with TemporaryDirectory() as tmp_dir:
        temp_path = Path(tmp_dir)
        temp_path = temp_path / "test"

        temp_path.mkdir()

        model, data = build_model()

        interface = TensorFlowModel(model=model, sample_data=data)

        assert interface.data_type == DataType.Numpy

        interface.save(temp_path, False)

        # list files
        interface.model = None
        assert interface.model is None

        interface.load(
            temp_path,
            model=True,
            sample_data=True,
        )

        assert interface.model is not None
