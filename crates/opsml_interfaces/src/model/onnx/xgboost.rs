use crate::error::OnnxError;
use crate::model::base::utils::OnnxExtension;
use crate::model::onnx::OnnxSession;
use opsml_types::ModelType;
use pyo3::types::PyList;
use pyo3::types::{PyDict, PyTuple};
use pyo3::{IntoPyObjectExt, prelude::*};
use tracing::debug;

fn convert_to_onnxmltools_type<'py>(
    py: Python<'py>,
    initial_type: &Bound<'py, PyTuple>,
) -> Result<Bound<'py, PyTuple>, OnnxError> {
    let onnxml_tools_float_type = py
        .import("onnxmltools")
        .unwrap()
        .getattr("convert")?
        .getattr("common")?
        .getattr("data_types")?
        .getattr("FloatTensorType")?;

    let onnxml_tools_int_type = py
        .import("onnxmltools")
        .unwrap()
        .getattr("convert")?
        .getattr("common")?
        .getattr("data_types")?
        .getattr("Int64TensorType")?;

    let skl2onnx_float_type = py
        .import("skl2onnx")
        .unwrap()
        .getattr("common")?
        .getattr("data_types")?
        .getattr("FloatTensorType")?;

    let skl2onnx_int_type = py
        .import("skl2onnx")
        .unwrap()
        .getattr("common")?
        .getattr("data_types")?
        .getattr("Int64TensorType")?;

    // get 2nd item from tuple and check if it is a skl2onnx type
    let name = initial_type.get_item(0).unwrap();
    let data_type = initial_type.get_item(1).unwrap();
    let shape = data_type.getattr("shape")?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("shape", shape).unwrap();

    if data_type.is_instance(&skl2onnx_float_type)? {
        let new_type = onnxml_tools_float_type.call((), Some(&kwargs))?;
        let py_tuple = PyTuple::new(py, &[name, new_type])?;

        Ok(py_tuple)
    } else if data_type.is_instance(&skl2onnx_int_type)? {
        let new_type = onnxml_tools_int_type.call((), Some(&kwargs))?;
        let py_tuple = PyTuple::new(py, &[name, new_type])?;

        Ok(py_tuple)
    } else {
        Ok(initial_type.clone())
    }
}

pub struct XGBoostOnnxConverter {}

impl Default for XGBoostOnnxConverter {
    fn default() -> Self {
        Self::new()
    }
}

impl XGBoostOnnxConverter {
    pub fn new() -> Self {
        XGBoostOnnxConverter {}
    }

    fn get_onnx_session(
        &self,
        model_proto: &Bound<'_, PyAny>,
        feature_names: Vec<String>,
    ) -> Result<OnnxSession, OnnxError> {
        OnnxSession::from_model_proto(model_proto, Some(feature_names))
    }

    pub fn convert_model<'py, T>(
        &self,
        py: Python<'py>,
        model: &Bound<'py, PyAny>,
        model_type: &ModelType,
        sample_data: &T,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> Result<OnnxSession, OnnxError>
    where
        T: OnnxExtension,
    {
        let onnxmltools = py.import("onnxmltools").map_err(OnnxError::ImportError)?;

        let type_helper = py
            .import("skl2onnx")
            .unwrap()
            .getattr("algebra")
            .unwrap()
            .getattr("type_helper")
            .unwrap();

        debug!("Step 1: Guessing initial types");
        // returns a list of tuples with (1) name and (2) type
        let initial_types = type_helper
            .call_method1(
                "guess_initial_types",
                (sample_data.get_data_for_onnx(py, model_type)?,),
            )
            .unwrap();

        let initial_types = initial_types.cast::<PyList>()?;

        // iter over the list and convert each to a tuple
        // Newer versions of onnxmltools requires the use of onnxmltools data types and not skl2onnx data types
        // XGBoost onnx only supports FloatTensorType and Int64TensorType
        debug!("Step 1.1: Converting initial types to onnxmltools ONNX types");
        let initial_types = initial_types
            .iter()
            .map(|x| {
                let x = x.cast::<PyTuple>().unwrap();
                convert_to_onnxmltools_type(py, x)
            })
            .collect::<Result<Vec<_>, _>>()?
            .into_bound_py_any(py)?;

        debug!("Step 2: Converting XGBoost model to ONNX");
        let kwargs = kwargs.map_or(PyDict::new(py), |kwargs| kwargs.clone());
        kwargs.set_item("initial_types", initial_types).unwrap();

        let model_proto = onnxmltools
            .call_method("convert_xgboost", (model,), Some(&kwargs))
            .map_err(OnnxError::PyOnnxConversionError)?;

        debug!("Step 3: Extracting ONNX schema");
        let onnx_session = self.get_onnx_session(&model_proto, sample_data.get_feature_names(py)?);
        debug!("ONNX model conversion complete");

        onnx_session
    }
}
