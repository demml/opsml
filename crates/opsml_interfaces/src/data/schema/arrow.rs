use crate::error::DataInterfaceError;
use crate::types::{Feature, FeatureSchema};
use pyo3::prelude::*;
use pyo3::types::PyList;

pub struct ArrowSchemaValidator {}

impl ArrowSchemaValidator {
    //pub fn get_polars_feature(value: &Bound<'_, PyAny>) -> PyResult<Feature> {}

    pub fn generate_feature_map(
        data: &Bound<'_, PyAny>,
    ) -> Result<FeatureSchema, DataInterfaceError> {
        let schema = data.getattr("schema")?;

        let schema_names = schema.getattr("names")?.extract::<Vec<String>>()?;

        // get types, downcast to list, iterate and call str() on each element
        let schema_types = schema
            .getattr("types")?
            .cast::<PyList>()?
            .iter()
            .map(|x| Ok(x.str()?.to_string()))
            .collect::<Result<Vec<String>, PyErr>>()?;

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
            .collect::<Result<FeatureSchema, PyErr>>()?;

        Ok(feature_map)
    }
}
