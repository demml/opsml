from pathlib import Path
from opsml.model import OnnxModel

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

    input_name = sess.get_inputs()[0].name
    label_name = sess.get_outputs()[0].name
    pred_onx = sess.run(
        input_feed={input_name: X_test.astype(np.float32)},
        output_names=[label_name],
    )[0]

    interface = OnnxModel(model=onx, sample_data=X_train)
    interface.create_drift_profile("drift", X_train)

    result = interface.session.run(
        input_feed={input_name: X_test.astype(np.float32)},
        output_names=[label_name],
    )[0]

    assert np.array_equal(pred_onx, result)

    save_path = tmp_path / "test"
    save_path.mkdir()

    metadata = interface.save(save_path, None)
    assert metadata.version != "undefined"
    interface.session.session = None
    assert metadata.save_metadata.save_kwargs is None
    assert interface.session.session is None

    interface.load(save_path, metadata.save_metadata)
    assert interface.session.session is not None

    interface.session.run(
        input_feed={input_name: X_test.astype(np.float32)},
        output_names=[label_name],
    )[0]
