use crate::data::{
    DataInterface, DataInterfaceMetadata, DataInterfaceSaveMetadata, DataLoadKwargs,
    DataSaveKwargs, SqlLogic,
};
use opsml_types::DataInterfaceType;
use pyo3::prelude::*;
use scouter_client::DataProfile;
use std::collections::HashMap;
use std::path::PathBuf;

#[pyclass(extends=DataInterface, subclass)]
pub struct SqlData {}

#[pymethods]
impl SqlData {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (sql_logic, data_profile=None))]
    fn new(
        py: Python,
        sql_logic: SqlLogic,
        data_profile: Option<DataProfile>,
    ) -> PyResult<(Self, DataInterface)> {
        // check if data is a numpy array

        let mut data_interface =
            DataInterface::new(py, None, None, None, None, Some(sql_logic), data_profile)?;
        data_interface.interface_type = DataInterfaceType::Sql;

        Ok((SqlData {}, data_interface))
    }

    #[allow(unused_variables)]
    #[pyo3(signature = (path, save_kwargs = None))]
    pub fn save(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        save_kwargs: Option<DataSaveKwargs>,
    ) -> PyResult<DataInterfaceMetadata> {
        let sql_uri = self_.as_super().save_sql(path.clone())?;
        let data_profile_uri = if self_.as_super().data_profile.is_none() {
            None
        } else {
            Some(self_.as_super().save_data_profile(&path)?)
        };

        let save_metadata = DataInterfaceSaveMetadata::new(
            PathBuf::new(),
            sql_uri,
            data_profile_uri,
            None,
            save_kwargs,
        );

        // need to implement save logic for SqlLogic
        Ok(DataInterfaceMetadata::new(
            save_metadata,
            self_.as_super().schema.clone(),
            HashMap::new(),
            self_.as_super().sql_logic.clone(),
            self_.as_super().interface_type.clone(),
        ))
    }

    #[allow(unused_variables)]
    #[pyo3(signature = (path, load_kwargs=None))]
    pub fn load(
        &mut self,
        py: Python,
        path: PathBuf,
        load_kwargs: Option<DataLoadKwargs>,
    ) -> PyResult<()> {
        Ok(())
    }
}
