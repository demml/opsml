import tensorflow as tf  # type: ignore
from typing import Tuple
import numpy as np
import sys
from tests.conftest import EXCLUDE
import pytest

IS_312 = sys.version_info >= (3, 12)


@pytest.mark.skipif((EXCLUDE or IS_312), reason="skipping")
def test_tensorflow_model(tf_sequential_model: Tuple[tf.keras.Sequential, np.ndarray]):
    model, data = tf_sequential_model

    print(model)
