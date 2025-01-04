use crate::data::DataInterface;
use crate::data::SqlLogic;
use crate::types::FeatureMap;
use opsml_error::OpsmlError;
use opsml_types::{SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use std::path::PathBuf;

#[pyclass(extends=DataInterface, subclass)]
pub struct NumpyData {}

#[pymethods]
impl NumpyData {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, feature_map=None, sql_logic=None))]
    fn new(
        py: Python,
        data: Option<&Bound<'_, PyAny>>, // data can be any pyobject
        data_splits: Option<&Bound<'_, PyAny>>, //
        dependent_vars: Option<&Bound<'_, PyAny>>,
        feature_map: Option<FeatureMap>,
        sql_logic: Option<SqlLogic>,
    ) -> PyResult<(Self, DataInterface)> {
        // check if data is a numpy array
        let data = match data {
            Some(data) => {
                // check if data is a numpy array
                // get type name of data
                let data_type = data
                    .get_type()
                    .name()
                    .map_err(|e| OpsmlError::new_err(e.to_string()))?;

                // check if data is a numpy array
                if data_type.to_string_lossy().to_lowercase() == "ndarray" {
                    Some(data)
                } else {
                    return Err(OpsmlError::new_err("Data must be a numpy array"));
                }
            }
            None => None,
        };

        let data_interface = DataInterface::new(
            py,
            data,
            data_splits,
            dependent_vars,
            feature_map,
            sql_logic,
        )?;
        Ok((NumpyData {}, data_interface))
    }

    #[setter]
    pub fn set_data(mut self_: PyRefMut<'_, Self>, data: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = data.py();
        let super_ = self_.as_super();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            super_.data = py.None();
            return Ok(());
        } else {
            // check if data is a numpy array
            // get type name of data
            let data_type = data
                .get_type()
                .name()
                .map_err(|e| OpsmlError::new_err(e.to_string()))?;

            // check if data is a numpy array
            if data_type.to_string_lossy().to_lowercase() != "ndarray" {
                return Err(OpsmlError::new_err("Data must be a numpy array"));
            }
            super_.data = data.into_py_any(py)?;
        };

        Ok(())
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save_data(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        // check if data is None
        let super_ = self_.as_super();

        if super_.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = path.join(SaveName::Data).with_extension(Suffix::Numpy);

        let numpy = py.import("numpy")?;
        let args = (&super_.data, save_path);

        // Save the data using joblib
        numpy.call_method("save", args, kwargs)?;

        // Get the class name of self.data
        let name: String = super_
            .data
            .getattr(py, "__class__")?
            .getattr(py, "__name__")?
            .extract(py)?;

        // Create and insert the feature
        //let mut features = HashMap::new();
        //features.insert("features".to_string(), Feature::new(name, vec![1], None));
        //self.feature_map = FeatureMap::new(Some(features));

        Ok(())
    }
}
