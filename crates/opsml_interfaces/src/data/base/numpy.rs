use crate::data::{generate_feature_schema, DataInterface, DataInterfaceSaveMetadata, SqlLogic};
use crate::types::FeatureMap;
use opsml_error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use std::path::PathBuf;

#[pyclass(extends=DataInterface, subclass)]
pub struct NumpyData {
    #[pyo3(get)]
    pub data_type: DataType,

    #[pyo3(get, set)]
    pub data: PyObject,
}

#[pymethods]
impl NumpyData {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, feature_map=None, sql_logic=None))]
    fn new<'py>(
        py: Python,
        data: Option<&Bound<'py, PyAny>>, // data can be any pyobject
        data_splits: Option<&Bound<'py, PyAny>>, //
        dependent_vars: Option<&Bound<'py, PyAny>>,
        feature_map: Option<FeatureMap>,
        sql_logic: Option<SqlLogic>,
    ) -> PyResult<(Self, DataInterface)> {
        // check if data is a numpy array
        let data = match data {
            Some(data) => {
                // check if data is a numpy array
                // get type name of data
                let numpy = py.import("numpy")?.getattr("ndarray")?;
                // check if data is a numpy array
                if data.is_instance(&numpy).unwrap() {
                    data.into_py_any(py)?
                } else {
                    return Err(OpsmlError::new_err("Data must be a numpy array"));
                }
            }
            None => py.None(),
        };

        let data_interface = DataInterface::new(
            py,
            None,
            data_splits,
            dependent_vars,
            feature_map,
            sql_logic,
        )?;

        Ok((
            NumpyData {
                data_type: DataType::Numpy,

                data,
            },
            data_interface,
        ))
    }

    #[setter]
    pub fn set_data<'py>(&mut self, data: &Bound<'py, PyAny>) -> PyResult<()> {
        let py = data.py();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            self.data = py.None();
            return Ok(());
        } else {
            // check if data is a numpy array
            // get type name of data
            let numpy = py.import("numpy")?.getattr("ndarray")?;

            // check if data is a numpy array
            if data.is_instance(&numpy).unwrap() {
                self.data = data.into_py_any(py)?;
                return Ok(());
            } else {
                return Err(OpsmlError::new_err("Data must be a numpy array"));
            }
        };
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save_data<'py>(
        &self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<PathBuf> {
        if self.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Numpy);
        let full_save_path = path.join(&save_path);

        let numpy = py.import("numpy")?;
        let args = (full_save_path, &self.data);

        // Save the data using joblib
        numpy
            .call_method("save", args, kwargs)
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        Ok(save_path)
    }

    /// Create a feature schema
    ///
    /// # Arguments
    ///
    /// * `name` - Name of the feature
    ///
    /// # Returns
    ///
    /// * `PyResult<FeatureMap>` - FeatureMap
    pub fn create_feature_map(&mut self, py: Python) -> PyResult<FeatureMap> {
        // Create and insert the feature
        generate_feature_schema(&self.data.bind(py), &self.data_type)
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<DataInterfaceSaveMetadata> {
        let save_path = self_.save_data(py, path.clone(), kwargs)?;
        let feature_map = self_.create_feature_map(py)?;

        let super_ = self_.as_super();
        let sql_save_path = super_.save_sql(path.clone())?;
        super_.feature_map = feature_map;

        Ok(DataInterfaceSaveMetadata {
            data_type: DataType::Numpy,
            feature_map: super_.feature_map.clone(),
            data_save_path: Some(save_path),
            sql_save_path: sql_save_path,
            data_profile_save_path: None,
        })
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn load_data<'py>(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Numpy);

        let numpy = PyModule::import(py, "numpy")?;

        // Load the data using numpy
        let data = numpy.call_method("load", (load_path,), kwargs)?;

        self.data = data.into();

        Ok(())
    }
}
