use crate::types::{Feature, FeatureMap};
use pyo3::prelude::*;

pub struct ArrowSchemaValidator {}

impl ArrowSchemaValidator {
    //pub fn get_polars_feature(value: &Bound<'_, PyAny>) -> PyResult<Feature> {}

    pub fn generate_feature_map(data: &Bound<'_, PyAny>) -> PyResult<FeatureMap> {
        let schema = data.getattr("schema")?;
        let schema_names = schema.getattr("names")?.extract::<Vec<String>>()?;
        let schema_types = schema.getattr("types")?.extract::<Vec<String>>()?;

        let feature_map = schema_names
            .iter()
            .zip(schema_types.iter())
            .map(|(name, data_type)| {
                let data_shape = vec![1];

                Ok((
                    name.to_string(),
                    Feature::new(data_type.to_string(), data_shape, None),
                ))
            })
            .collect::<Result<FeatureMap, PyErr>>()?;

        Ok(feature_map)
    }
}
