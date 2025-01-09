use crate::types::FeatureSchema;

use crate::data::schema::arrow::ArrowSchemaValidator;
use crate::data::schema::numpy::NumpySchemaValidator;
use crate::data::schema::pandas::PandasSchemaValidator;
use crate::data::schema::polars::PolarsSchemaValidator;
use crate::data::schema::torch::TorchTensorSchemaValidator;
use opsml_types::DataType;
use pyo3::prelude::*;

#[pyfunction]
pub fn generate_feature_schema(
    data: &Bound<'_, PyAny>,
    data_type: &DataType,
) -> PyResult<FeatureSchema> {
    let feature_map = match data_type {
        DataType::Polars => PolarsSchemaValidator::generate_feature_map(data)?,
        DataType::Numpy => NumpySchemaValidator::generate_feature_map(data)?,
        DataType::Pandas => PandasSchemaValidator::generate_feature_map(data)?,
        DataType::Arrow => ArrowSchemaValidator::generate_feature_map(data)?,
        DataType::TorchTensor => TorchTensorSchemaValidator::generate_feature_map(data)?,

        _ => FeatureSchema::new(None),
    };
    Ok(feature_map)
}
