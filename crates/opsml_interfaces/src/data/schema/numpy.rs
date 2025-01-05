use crate::types::{Feature, FeatureMap};
use pyo3::prelude::*;

pub struct NumpySchemaValidator {}

impl NumpySchemaValidator {
    //pub fn get_polars_feature(value: &Bound<'_, PyAny>) -> PyResult<Feature> {}

    pub fn generate_feature_map(data: &Bound<'_, PyAny>) -> PyResult<FeatureMap> {
        let mut feature_map = FeatureMap::new(None);

        let data_type = data.getattr("dtype")?.str()?.to_string();
        let data_shape = data.getattr("shape")?.extract::<Vec<usize>>()?;

        feature_map.map.insert(
            "numpy_array".to_string(),
            Feature::new(data_type.to_string(), data_shape, None),
        );

        Ok(feature_map)
    }
}
