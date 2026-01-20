use crate::error::DataInterfaceError;
use crate::types::{Feature, FeatureSchema};
use pyo3::prelude::*;
use pyo3::types::PyDict;

pub struct PandasSchemaValidator {}

impl PandasSchemaValidator {
    //pub fn get_polars_feature(value: &Bound<'_, PyAny>) -> PyResult<Feature> {}

    pub fn generate_feature_map(
        data: &Bound<'_, PyAny>,
    ) -> Result<FeatureSchema, DataInterfaceError> {
        let columns = data.getattr("dtypes")?.call_method0("to_dict")?;
        let columns = columns.cast::<PyDict>()?;

        let feature_map = columns
            .iter()
            .map(|(key, value)| {
                let data_type = value.str()?.to_string();
                let data_shape = vec![1];

                Ok((key.to_string(), Feature::new(data_type, data_shape, None)))
            })
            .collect::<Result<FeatureSchema, PyErr>>()?;

        Ok(feature_map)
    }
}
