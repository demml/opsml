use crate::types::FeatureMap;

use crate::data::schema::polars::PolarsSchemaValidator;
use opsml_types::DataType;
use pyo3::prelude::*;

#[pyfunction]
pub fn generate_feature_schema<'py>(
    data: &Bound<'py, PyAny>,
    data_type: &DataType,
) -> PyResult<FeatureMap> {
    let feature_map = match data_type {
        DataType::Polars => PolarsSchemaValidator::generate_feature_map(data)?,
        _ => FeatureMap::new(None),
    };
    Ok(feature_map)
}
