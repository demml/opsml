use crate::types::{Feature, FeatureMap};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;

pub struct PandasSchemaValidator {}

impl PandasSchemaValidator {
    //pub fn get_polars_feature(value: &Bound<'_, PyAny>) -> PyResult<Feature> {}

    pub fn generate_feature_map(data: &Bound<'_, PyAny>) -> PyResult<FeatureMap> {
        let columns = data.getattr("dtypes")?.call_method0("to_dict")?;
        let columns = columns.downcast::<PyDict>()?;

        let features = columns
            .iter()
            .map(|(key, value)| {
                let data_type = value.str()?.to_string();
                let data_shape = vec![1];

                Ok((key.to_string(), Feature::new(data_type, data_shape, None)))
            })
            .collect::<Result<HashMap<String, Feature>, PyErr>>()?;

        let feature_map = FeatureMap::new(Some(features));

        Ok(feature_map)
    }
}
