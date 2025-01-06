use crate::data::{generate_feature_schema, DataInterface, InterfaceSaveMetadata, SqlLogic};
use crate::types::FeatureMap;
use opsml_error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use std::path::PathBuf;

#[pyclass(extends=DataInterface, subclass)]
pub struct ArrowData {
    #[pyo3(get)]
    pub data_type: DataType,

    #[pyo3(get, set)]
    pub data: PyObject,
}

#[pymethods]
impl ArrowData {
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
                let pyarrow_table = py.import("pyarrow")?.getattr("Table")?;
                // check if data is a numpy array
                if data.is_instance(&pyarrow_table).unwrap() {
                    data.into_py_any(py)?
                } else {
                    return Err(OpsmlError::new_err("Data must be a pyarrow table"));
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
            ArrowData {
                data_type: DataType::Arrow,

                data,
            },
            data_interface,
        ))
    }

    #[setter]
    pub fn set_data(&mut self, data: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = data.py();

        // check if data is None
        if PyAnyMethods::is_none(data) {
            self.data = py.None();
            return Ok(());
        } else {
            // check if data is a numpy array
            // get type name of data
            let pyarrow_table = py.import("pyarrow")?.getattr("Table")?;

            // check if data is a numpy array
            if data.is_instance(&pyarrow_table).unwrap() {
                self.data = data.into_py_any(py)?;
                return Ok(());
            } else {
                return Err(OpsmlError::new_err("Data must be a pyarrow table"));
            }
        };
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save_data(
        &self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<PathBuf> {
        if self.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Parquet);
        let full_save_path = path.join(&save_path);

        let parquet = py.import("pyarrow")?.getattr("parquet")?;
        let args = (&self.data, full_save_path);

        // Save the data using joblib
        parquet
            .call_method("write_table", args, kwargs)
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

    #[pyo3(signature = (path, kwargs=None))]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<InterfaceSaveMetadata> {
        let save_path = self_.save_data(py, path.clone(), kwargs)?;
        let feature_map = self_.create_feature_map(py)?;

        let super_ = self_.as_super();
        let sql_save_path = super_.save_sql(path.clone())?;
        super_.feature_map = feature_map;

        Ok(InterfaceSaveMetadata {
            data_type: DataType::Arrow,
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
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);

        let parquet = py.import("pyarrow")?.getattr("parquet")?;

        // Load the data using numpy
        let data = parquet.call_method("read_table", (load_path,), kwargs)?;

        self.data = data.into();

        Ok(())
    }
}
