use crate::data::{
    schema::generate_feature_schema, DataInterface, InterfaceSaveMetadata, SqlLogic,
};
use crate::types::FeatureMap;
use opsml_error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use std::path::PathBuf;

#[pyclass(extends=DataInterface, subclass)]
pub struct PolarsData {
    #[pyo3(get)]
    pub data_type: DataType,

    #[pyo3(get, set)]
    pub data: PyObject,
}

#[pymethods]
impl PolarsData {
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
                // import polars.DataFrame and check if data is a polars.DataFrame
                let polars = PyModule::import(py, "polars")?;
                let polars_data_frame = polars.getattr("DataFrame")?;

                // check if data is a polars.DataFrame
                if data.is_instance(&polars_data_frame).unwrap() {
                    data.into_py_any(py)?
                } else {
                    return Err(OpsmlError::new_err("Data must be a polars.DataFrame"));
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
            PolarsData {
                data_type: DataType::Polars,

                data,
            },
            data_interface,
        ))
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<InterfaceSaveMetadata> {
        // check if data is None

        if self_.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        // Save the data using parquet
        let feature_map = generate_feature_schema(self_.data.bind(py), &DataType::Polars)?;

        let save_path = PathBuf::from(SaveName::Data.to_string()).with_extension(Suffix::Parquet);
        let full_save_path = path.join(&save_path);

        let _ = self_
            .data
            .call_method(py, "write_parquet", (full_save_path,), kwargs)
            .map_err(|e| OpsmlError::new_err(e.to_string()))?;

        let super_ = self_.as_super();
        super_.feature_map = feature_map.clone();

        Ok(InterfaceSaveMetadata {
            data_type: self_.data_type.clone(),
            feature_map,
            data_save_path: Some(save_path),
            sql_save_path: None,
            data_profile_save_path: None,
        })
    }

    #[pyo3(signature = (path, **kwargs))]
    pub fn load<'py>(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        let load_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);

        let polars = PyModule::import(py, "polars")?;

        // Load the data using polars
        let data = polars.call_method("read_parquet", (load_path,), kwargs)?;

        self.data = data.into();

        Ok(())
    }
}
