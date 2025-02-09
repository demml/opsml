use crate::data::{DataInterface, DataInterfaceSaveMetadata, SqlLogic};
use crate::types::FeatureSchema;
use opsml_error::OpsmlError;
use opsml_types::{DataInterfaceType, DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use scouter_client::DataProfile;
use std::path::{Path, PathBuf};

#[pyclass(extends=DataInterface, subclass)]
#[derive(Debug, Clone)]
pub struct PandasData {}

#[pymethods]
impl PandasData {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (data=None, data_splits=None, dependent_vars=None, feature_map=None, sql_logic=None, data_profile=None))]
    pub fn new<'py>(
        py: Python,
        data: Option<&Bound<'py, PyAny>>, // data can be any pyobject
        data_splits: Option<&Bound<'py, PyAny>>, //
        dependent_vars: Option<&Bound<'py, PyAny>>,
        feature_map: Option<FeatureSchema>,
        sql_logic: Option<SqlLogic>,
        data_profile: Option<DataProfile>,
    ) -> PyResult<(Self, DataInterface)> {
        // check if data is a numpy array
        let data = match data {
            Some(data) => {
                // check if data is a numpy array
                // get type name of data
                let pandas = py.import("pandas")?.getattr("DataFrame")?;

                // check if data is a numpy array
                if data.is_instance(&pandas).unwrap() {
                    data.into_py_any(py)?
                } else {
                    return Err(OpsmlError::new_err("Data must be a pandas dataframe"));
                }
            }
            None => py.None(),
        };

        let mut data_interface = DataInterface::new(
            py,
            None,
            data_splits,
            dependent_vars,
            feature_map,
            sql_logic,
            data_profile,
        )?;

        data_interface.data_type = DataType::Pandas;
        data_interface.data = data;
        data_interface.interface_type = DataInterfaceType::Pandas;

        Ok((PandasData {}, data_interface))
    }

    #[getter]
    pub fn get_data(self_: PyRef<'_, Self>, py: Python) -> PyObject {
        self_.as_super().data.clone_ref(py)
    }

    #[setter]
    pub fn set_data<'py>(mut self_: PyRefMut<'py, Self>, data: &Bound<'py, PyAny>) -> PyResult<()> {
        let py = data.py();
        let parent = self_.as_super();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            parent.data = py.None();
            Ok(())
        } else {
            // check if data is a numpy array
            // get type name of data
            let pandas = py.import("pandas")?.getattr("DataFrame")?;

            // check if data is a numpy array
            if data.is_instance(&pandas).unwrap() {
                parent.data = data.into_py_any(py)?;
                Ok(())
            } else {
                Err(OpsmlError::new_err("Data must be a pandas DataFrame"))
            }
        }
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save_data<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<PathBuf> {
        // check if data is None

        let parent = self_.as_super();
        if parent.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Parquet);
        let full_save_path = path.join(&save_path);

        let _ = &parent
            .data
            .call_method(py, "to_parquet", (full_save_path,), kwargs)
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        Ok(save_path)
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<DataInterfaceSaveMetadata> {
        let feature_map = self_.as_super().create_feature_map(py)?;
        let sql_save_path = self_.as_super().save_sql(path.clone())?;
        let save_path = PandasData::save_data(self_, py, path.clone(), kwargs)?;

        Ok(DataInterfaceSaveMetadata {
            data_type: DataType::Pandas,
            feature_map: feature_map.clone(),
            data_save_path: Some(save_path),
            sql_save_path,
            data_profile_save_path: None,
        })
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn load_data<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);

        let pandas = PyModule::import(py, "pandas")?;

        // Load the data using polars
        let data = pandas.call_method("read_parquet", (load_path,), kwargs)?;

        self_.as_super().data = data.into();

        Ok(())
    }
}

impl PandasData {
    pub fn from_path(
        py: Python,
        path: &Path,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PyObject> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);

        let pandas = PyModule::import(py, "pandas")?;

        // Load the data using polars
        let data = pandas.call_method("read_parquet", (load_path,), kwargs)?;

        let interface = PandasData::new(py, Some(&data), None, None, None, None, None)?;

        let bound = Py::new(py, interface)?.as_any().clone_ref(py);

        Ok(bound)
    }
}
