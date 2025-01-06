use crate::data::{DataInterface, DataInterfaceSaveMetadata, SqlLogic};
use crate::types::FeatureMap;
use opsml_error::OpsmlError;
use opsml_types::DataType;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::PathBuf;

#[pyclass(extends=DataInterface, subclass)]
pub struct SqlData {
    #[pyo3(get)]
    pub data_type: DataType,
}

#[pymethods]
impl SqlData {
    #[new]
    #[allow(clippy::too_many_arguments)]
    fn new(py: Python, sql_logic: SqlLogic) -> PyResult<(Self, DataInterface)> {
        // check if data is a numpy array

        let data_interface = DataInterface::new(py, None, None, None, None, Some(sql_logic))?;

        Ok((
            SqlData {
                data_type: DataType::Sql,
            },
            data_interface,
        ))
    }

    #[allow(unused_variables)]
    #[setter]
    fn set_data<'py>(&mut self, data: &Bound<'py, PyAny>) -> PyResult<()> {
        // this should return an error. Data cannot be set for SqlData
        Err(OpsmlError::new_err("Data cannot be set for SqlData"))
    }

    #[allow(unused_variables)]
    #[pyo3(signature = (path, **kwargs))]
    pub fn save<'py>(
        mut self_: PyRefMut<'py, Self>,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<DataInterfaceSaveMetadata> {
        let super_ = self_.as_super();
        let sql_save_path = super_.save_sql(path)?;

        // need to implement save logic for SqlLogic
        Ok(DataInterfaceSaveMetadata {
            data_type: self_.data_type.clone(),
            feature_map: FeatureMap::default(),
            data_save_path: None,
            sql_save_path: sql_save_path,
            data_profile_save_path: None,
        })
    }

    #[allow(unused_variables)]
    #[pyo3(signature = (path, **kwargs))]
    pub fn load_data<'py>(
        &mut self,
        py: Python,
        path: PathBuf,
        kwargs: Option<&Bound<'py, PyDict>>,
    ) -> PyResult<()> {
        Ok(())
    }
}
