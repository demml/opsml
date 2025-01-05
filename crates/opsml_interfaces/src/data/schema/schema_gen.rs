use crate::types::FeatureMap;

use crate::data::schema::numpy::NumpySchemaValidator;
use crate::data::schema::pandas::PandasSchemaValidator;
use crate::data::schema::polars::PolarsSchemaValidator;
use opsml_types::DataType;
use pyo3::prelude::*;

#[pyfunction]
pub fn generate_feature_schema(
    data: &Bound<'_, PyAny>,
    data_type: &DataType,
) -> PyResult<FeatureMap> {
    let feature_map = match data_type {
        DataType::Polars => PolarsSchemaValidator::generate_feature_map(data)?,
        DataType::Numpy => NumpySchemaValidator::generate_feature_map(data)?,
        DataType::Pandas => PandasSchemaValidator::generate_feature_map(data)?,
        _ => FeatureMap::new(None),
    };
    Ok(feature_map)
}
