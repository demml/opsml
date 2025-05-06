from typing import Tuple
import warnings
from pathlib import Path
from opsml.model import SklearnModel, OnnxSession, ModelInterfaceMetadata
from opsml.data import NumpyData

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from skl2onnx import to_onnx


def test_onnx_model(tmp_path: Path):
    iris = load_iris()

    X, y = iris.data, iris.target
    X = X.astype(np.float32)
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    clr = RandomForestClassifier()
    clr.fit(X_train, y_train)
