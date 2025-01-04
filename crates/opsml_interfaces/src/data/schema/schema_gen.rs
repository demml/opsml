use crate::types::{Feature, FeatureMap};

use opsml_types::DataType;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};
use std::collections::HashMap;
pub struct PolarsStructType {}

impl PolarsStructType {
    fn as_feature(data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let fields = data_type.getattr("fields")?;
        let fields = fields.downcast::<PyList>()?;

        let extras_args = fields
            .iter()
            .map(|field| {
                let field_name = field.getattr("name")?.extract::<String>()?;
                let field_type = field.getattr("dtype")?.str()?.to_string();
                Ok((field_name, field_type))
            })
            .collect::<PyResult<HashMap<String, String>>>()?;

        let tuple_shape = data_type.getattr("shape")?;
        let tuple_shape = tuple_shape.downcast::<PyTuple>()?;

        let shape = tuple_shape
            .iter()
            .map(|x| x.extract::<i32>())
            .collect::<PyResult<Vec<i32>>>()?;

        let feature = Feature::new("struct".to_string(), vec![1], Some(extras_args));
        Ok(feature)
    }
}

pub struct DefaultPolarsType {}

impl DefaultPolarsType {
    fn as_feature(data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new(data_type.str().unwrap().to_string(), vec![1], None);
        Ok(feature)
    }
}

struct PolarsSchemaValidator {}

impl PolarsSchemaValidator {
    pub fn get_polars_feature(value: &Bound<'_, PyAny>) -> PyResult<Feature> {}

    pub fn generate_feature_map(data: &Bound<'_, PyAny>) -> PyResult<HashMap<String, Feature>> {
        let mut feature_map = FeatureMap::new(None);

        let schema = data.as_ref().getattr("schema")?;
        // get schema items dict
        let schema_items = schema.getattr("items")?.downcast::<PyDict>()?;

        for (key, value) in schema_items.iter() {
            let column_type = column.getattr("type")?.extract::<String>()?;
            let column_shape = column.getattr("shape")?.extract::<Vec<i32>>()?;
            let column_extra_args = column
                .getattr("extra_args")?
                .extract::<HashMap<String, String>>()?;

            let feature = Feature::new(column_type, column_shape, Some(column_extra_args));
            feature_map.map.insert(column_name.to_string(), feature);
        }

        Ok(feature_map)
    }
}

#[pyfunction]
pub fn generate_feature_schema(data: &Bound<'_, PyAny>, data_type: &DataType) -> PyResult<()> {
    Ok(())
}
