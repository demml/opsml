use opsml_types::ModelType;
use pyo3::ffi::c_str;
use pyo3::types::{PyDict, PyList};
use pyo3::{IntoPyObjectExt, prelude::*};

pub struct LightGBMRegistryUpdater {}

impl LightGBMRegistryUpdater {
    fn get_output_tools<'py>(
        py: Python<'py>,
        model_type: &ModelType,
    ) -> PyResult<Bound<'py, PyAny>> {
        let shape_calculator = py
            .import("skl2onnx")?
            .getattr("common")?
            .getattr("shape_calculator")?;

        let calculate_linear_classifier_output_shapes =
            shape_calculator.getattr("calculate_linear_classifier_output_shapes")?;

        let calculate_linear_regressor_output_shapes =
            shape_calculator.getattr("calculate_linear_regressor_output_shapes")?;

        match model_type {
            ModelType::LgbmRegressor => Ok(calculate_linear_regressor_output_shapes),
            ModelType::LgbmClassifier => Ok(calculate_linear_classifier_output_shapes),
            _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Model type not supported",
            )),
        }
    }

    fn get_options(py: Python, model_type: &ModelType) -> PyResult<Py<PyAny>> {
        // make new pydict {"nocl": [True, False], "zipmap": [True, False, "columns"]}

        match model_type {
            ModelType::LgbmClassifier => {
                let pydict = PyDict::new(py);

                let nocl_list = PyList::new(py, vec![true, false])?;
                let zipmap_list = PyList::new(py, vec![true, false])?;
                zipmap_list.append("columns")?;

                pydict.set_item("nocl", nocl_list)?;
                pydict.set_item("zipmap", zipmap_list)?;

                pydict.into_py_any(py)
            }
            _ => Ok(py.None()),
        }
    }

    pub fn update_registry(py: Python, model_type: &ModelType) -> PyResult<()> {
        let lgb = py.import("lightgbm")?;

        let locals = PyDict::new(py);
        py.run(
            c_str!(
                r#"
from onnxmltools.convert.lightgbm.operator_converters.LightGbm import convert_lightgbm
"#
            ),
            None,
            Some(&locals),
        )
        .unwrap();

        let convert_lightgbm = locals.get_item("convert_lightgbm")?.unwrap();

        let update_registered_converter = py
            .import("skl2onnx")?
            .getattr("update_registered_converter")?;

        let model_class = lgb.getattr(model_type.to_string())?;
        let output_shape_calculator = Self::get_output_tools(py, model_type)?;
        let options = Self::get_options(py, model_type)?;

        let args = (
            model_class,
            model_type.to_string(),
            output_shape_calculator,
            convert_lightgbm,
            true,
            py.None(),
            options,
        );

        update_registered_converter.call(args, None)?;

        Ok(())
    }
}

pub struct XGBoostRegistryUpdater {}

impl XGBoostRegistryUpdater {
    fn get_output_tools<'py>(
        py: Python<'py>,
        model_type: &ModelType,
    ) -> PyResult<Bound<'py, PyAny>> {
        let shape_calculator = py
            .import("skl2onnx")?
            .getattr("common")?
            .getattr("shape_calculator")?;

        let calculate_linear_classifier_output_shapes =
            shape_calculator.getattr("calculate_linear_classifier_output_shapes")?;

        let calculate_linear_regressor_output_shapes =
            shape_calculator.getattr("calculate_linear_regressor_output_shapes")?;

        match model_type {
            ModelType::XgbRegressor => Ok(calculate_linear_regressor_output_shapes),
            ModelType::XgbClassifier => Ok(calculate_linear_classifier_output_shapes),
            _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Model type not supported",
            )),
        }
    }

    fn get_options(py: Python, model_type: &ModelType) -> PyResult<Py<PyAny>> {
        // make new pydict {"nocl": [True, False], "zipmap": [True, False, "columns"]}

        match model_type {
            ModelType::XgbClassifier => {
                let pydict = PyDict::new(py);

                let nocl_list = PyList::new(py, vec![true, false])?;
                let zipmap_list = PyList::new(py, vec![true, false])?;
                zipmap_list.append("columns")?;

                pydict.set_item("nocl", nocl_list)?;
                pydict.set_item("zipmap", zipmap_list)?;

                pydict.into_py_any(py)
            }
            _ => Ok(py.None()),
        }
    }

    pub fn update_registry(py: Python, model_type: &ModelType) -> PyResult<()> {
        // registry update only applies to XGBClassifier

        let xgb = py.import("xgboost")?;

        let locals = PyDict::new(py);
        py.run(
            c_str!(
                r#"
from onnxmltools.convert.xgboost.operator_converters.XGBoost import convert_xgboost
"#
            ),
            None,
            Some(&locals),
        )
        .unwrap();

        let convert_xgboost = locals.get_item("convert_xgboost")?.unwrap();

        let update_registered_converter = py
            .import("skl2onnx")?
            .getattr("update_registered_converter")?;

        let model_class = xgb.getattr(model_type.to_string())?;
        let output_shape_calculator = Self::get_output_tools(py, model_type)?;
        let options = Self::get_options(py, model_type)?;

        let args = (
            model_class,
            model_type.to_string(),
            output_shape_calculator,
            convert_xgboost,
            true,
            py.None(),
            options,
        );

        update_registered_converter.call(args, None)?;

        Ok(())
    }
}

pub struct OnnxRegistryUpdater {}

impl OnnxRegistryUpdater {
    pub fn update_registry(py: Python, model_type: &ModelType) -> PyResult<()> {
        match model_type {
            ModelType::LgbmClassifier | ModelType::LgbmRegressor => {
                LightGBMRegistryUpdater::update_registry(py, model_type)
            }
            ModelType::XgbClassifier | ModelType::XgbRegressor => {
                XGBoostRegistryUpdater::update_registry(py, model_type)
            }
            _ => Ok(()),
        }
    }
}
