from opsml.registry.model.interfaces.sklearn import SklearnModel


class XGBoostModel(SklearnModel):
    """Model interface for XGBoost model class. Currently, only Sklearn flavor of XGBoost
    regressor and classifier are supported.

    Args:
        model:
            XGBoost model
        preprocessor:
            Optional preprocessor
        sample_data:
            Sample data to be used for type inference and ONNX conversion/validation.
            This should match exactly what the model expects as input. See example below.
        task_type:
            Task type for model. Defaults to undefined.
        model_type:
            Optional model type. This is inferred automatically.
        preprocessor_name:
            Optional preprocessor. This is inferred automatically if a
            preprocessor is provided.

    Returns:
        XGBoostModel
    """

    ...
