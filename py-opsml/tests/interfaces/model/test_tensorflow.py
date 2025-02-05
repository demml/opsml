import tensorflow as tf  # type: ignore
import numpy as np


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
    model, data = build_model()
