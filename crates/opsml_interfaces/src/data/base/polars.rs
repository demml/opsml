use crate::data::schema::generate_feature_schema;
use crate::data::DataInterface;
use crate::data::SqlLogic;
use crate::types::FeatureMap;
use opsml_error::OpsmlError;
use opsml_types::{DataType, SaveName, Suffix};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::PathBuf;

#[pyclass(extends=DataInterface, subclass)]
pub struct PolarsData {
    #[pyo3(get)]
    pub data_type: DataType,
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
                    Some(data)
                } else {
                    return Err(OpsmlError::new_err("Data must be a polars.DataFrame"));
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
        Ok((
            PolarsData {
                data_type: DataType::Polars,
            },
            data_interface,
        ))
    }

    #[pyo3(signature = (path, **py_kwargs))]
    pub fn save_data(
        mut self_: PyRefMut<'_, Self>,
        py: Python,
        path: PathBuf,
        py_kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        // check if data is None
        let super_ = self_.as_super();

        if super_.data.is_none(py) {
            return Err(OpsmlError::new_err(
                "No data detected in interface for saving",
            ));
        }

        println!("kwargs {:?}", py_kwargs);

        // Save the data using parquet
        generate_feature_schema(&super_.data.bind(py), &DataType::Polars)?;

        //let save_path = path.join(SaveName::Data).with_extension(Suffix::Parquet);

        //let _ = &super_
        //    .data
        //    .call_method(py, "write_parquet", (save_path,), py_kwargs)
        //    .unwrap();

        // Create and insert the feature
        //let mut features = HashMap::new();
        //features.insert("features".to_string(), Feature::new(name, vec![1], None));
        //self.feature_map = FeatureMap::new(Some(features));

        Ok(())
    }
}
