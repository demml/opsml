from typing import Tuple
import warnings
from pathlib import Path
from opsml.model import OnnxModel, OnnxSession, ModelInterfaceMetadata
from opsml.data import NumpyData

import numpy as np
from sklearn.datasets import load_iris  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.ensemble import RandomForestClassifier  # type: ignore
from skl2onnx import to_onnx  # type: ignore
import onnxruntime as rt  # type: ignore


def test_onnx_model(tmp_path: Path):
    iris = load_iris()

    X, y = iris.data, iris.target
    X = X.astype(np.float32)
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    clr = RandomForestClassifier()
    clr.fit(X_train, y_train)

    onx = to_onnx(clr, X[:1])

    # save the model to a file
    onnx_model_path = tmp_path / "model.onnx"
    with open(onnx_model_path, "wb") as f:
        f.write(onx.SerializeToString())

    # Load the model using OnnxModel

    sess = rt.InferenceSession(
        onnx_model_path.as_posix(),
        providers=["CPUExecutionProvider"],
    )

    interface_model = OnnxModel(session=sess)
