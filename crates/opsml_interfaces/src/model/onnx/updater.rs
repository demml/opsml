use crate::types::ModelType;
use pyo3::types::{PyDict, PyList};
use pyo3::{prelude::*, IntoPyObjectExt};

pub struct LightGBMRegistryUpdater {}

impl LightGBMRegistryUpdater {
    fn get_output_tools<'py>(
        py: Python<'py>,
        model_type: &ModelType,
    ) -> PyResult<(Bound<'py, PyAny>, Bound<'py, PyAny>)> {
        let shape_calculator = py
            .import("skl2onnx")?
            .getattr("common")?
            .getattr("shape_calculator")?;

        let calculate_linear_classifier_output_shapes =
            shape_calculator.getattr("calculate_linear_classifier_output_shapes")?;

        let calculate_linear_regressor_output_shapes =
            shape_calculator.getattr("calculate_linear_regressor_output_shapes")?;

        match model_type {
            ModelType::LgbmRegressor => Ok((
                calculate_linear_regressor_output_shapes,
                py.None().bind(py).clone(),
            )),
            ModelType::LgbmClassifier => {
                // make new pydict {"nocl": [True, False], "zipmap": [True, False, "columns"]}
                let pydict = PyDict::new(py);

                let nocl_list = PyList::new(py, vec![true, false])?;
                let zipmap_list = PyList::new(py, vec![true, false])?;
                zipmap_list.append("columns")?;

                pydict.set_item("nocl", nocl_list)?;
                pydict.set_item("zipmap", zipmap_list)?;

                Ok((
                    calculate_linear_classifier_output_shapes,
                    pydict.into_bound_py_any(py)?,
                ))
            }
            _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Model type not supported",
            )),
        }
    }

    pub fn update_registry<'py>(py: Python, model_type: &ModelType) -> PyResult<()> {
        let lgb = py.import("lightgbm")?;

        let convert_lightgbm = py
            .import("onnxmltools")?
            .getattr("convert")?
            .getattr("lightgbm")?
            .getattr("operator_converters")?
            .getattr("LightGbm")?
            .getattr("convert_lightgbm")?;

        let update_registered_converter = py
            .import("skl2onnx")?
            .getattr("update_registered_converter")?;

        let model_class = lgb.getattr(model_type.to_string())?;
        let (output_calculator, options) = Self::get_output_tools(py, model_type)?;

        let args = (
            model_class,
            model_type.to_string(),
            output_calculator,
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
            ModelType::LgbmClassifier => Ok(calculate_linear_classifier_output_shapes),
            _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Model type not supported",
            )),
        }
    }

    pub fn update_registry<'py>(py: Python, model_type: &ModelType) -> PyResult<()> {
        // registry update only applies to XGBClassifier
        if model_type != &ModelType::XgbClassifier {
            return Ok(());
        }

        let xgb = py.import("xgboost")?;

        let convert_lightgbm = py
            .import("onnxmltools")?
            .getattr("convert")?
            .getattr("lightgbm")?
            .getattr("operator_converters")?
            .getattr("XGBoost")?
            .getattr("convert_xgboost")?;

        let update_registered_converter = py
            .import("skl2onnx")?
            .getattr("update_registered_converter")?;

        let model_class = xgb.getattr(model_type.to_string())?;
        let output_calculator = Self::get_output_tools(py, model_type)?;

        let args = (
            model_class,
            model_type.to_string(),
            output_calculator,
            convert_lightgbm,
            true,
            py.None(),
            py.None(),
        );

        update_registered_converter.call(args, None)?;

        Ok(())
    }
}
