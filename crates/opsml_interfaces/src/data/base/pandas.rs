use crate::data::{DataInterface, DataInterfaceSaveMetadata, SqlLogic};
use crate::types::FeatureMap;
use opsml_error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use std::path::PathBuf;

#[pyclass(extends=DataInterface, subclass)]
pub struct PandasData {}

#[pymethods]
impl PandasData {
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
        )?;

        data_interface.data_type = DataType::Pandas;
        data_interface.data = data;

        Ok((PandasData {}, data_interface))
    }

    #[getter]
    pub fn get_data<'py>(self_: PyRef<'py, Self>, py: Python) -> PyObject {
        self_.as_super().data.clone_ref(py)
    }

    #[setter]
    pub fn set_data<'py>(mut self_: PyRefMut<'py, Self>, data: &Bound<'py, PyAny>) -> PyResult<()> {
        let py = data.py();
        let base = self_.as_super();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            base.data = py.None();
            return Ok(());
        } else {
            // check if data is a numpy array
            // get type name of data
            let pandas = py.import("pandas")?.getattr("DataFrame")?;

            // check if data is a numpy array
            if data.is_instance(&pandas).unwrap() {
                base.data = data.into_py_any(py)?;
                return Ok(());
            } else {
                return Err(OpsmlError::new_err("Data must be a pandas DataFrame"));
            }
        };
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save_data<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<PathBuf> {
        // check if data is None

        let base = self_.as_super();
        if base.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Parquet);
        let full_save_path = path.join(&save_path);

        let _ = &base
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
            sql_save_path: sql_save_path,
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
