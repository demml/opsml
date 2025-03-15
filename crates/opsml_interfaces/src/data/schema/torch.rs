use crate::types::{Feature, FeatureSchema};
use pyo3::prelude::*;

pub struct TorchTensorSchemaValidator {}

impl TorchTensorSchemaValidator {
    //pub fn get_polars_feature(value: &Bound<'_, PyAny>) -> PyResult<Feature> {}

    pub fn generate_feature_map(data: &Bound<'_, PyAny>) -> PyResult<FeatureSchema> {
        let shape = data.getattr("shape")?.extract::<Vec<i64>>()?;
        let data_type = data.getattr("dtype")?.str()?.to_string();
        let mut feature_map = FeatureSchema::new(None);

        feature_map.items.insert(
            "torch_tensor".to_string(),
            Feature::new(data_type, shape, None),
        );
        Ok(feature_map)
    }
}
