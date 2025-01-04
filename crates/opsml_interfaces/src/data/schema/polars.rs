use crate::types::{Feature, FeatureMap};

use opsml_types::DataType;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};
use std::collections::HashMap;

pub struct Int8 {}

impl Int8 {
    fn as_feature(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Int8".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let signed_int = py.import("polars")?.getattr("datatypes")?.getattr("Int8")?;

        let is_signed_int = data_type.is_instance(&signed_int)?;

        Ok(is_signed_int)
    }
}

pub struct Int16 {}

impl Int16 {
    fn as_feature(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Int16".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let signed_int = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Int16")?;

        let is_signed_int = data_type.is_instance(&signed_int)?;

        Ok(is_signed_int)
    }
}

pub struct Int32 {}

impl Int32 {
    fn as_feature(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Int32".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let signed_int = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Int32")?;

        let is_signed_int = data_type.is_instance(&signed_int)?;

        Ok(is_signed_int)
    }
}

pub struct Int64 {}

impl Int64 {
    fn as_feature(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Int64".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let signed_int = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Int64")?;

        let is_signed_int = data_type.is_instance(&signed_int)?;

        Ok(is_signed_int)
    }
}

pub struct UInt8 {}

impl UInt8 {
    fn as_feature(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("UInt8".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let unsigned_int = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("UInt8")?;

        let is_unsigned_int = data_type.is_instance(&unsigned_int)?;

        Ok(is_unsigned_int)
    }
}

pub struct UInt16 {}

impl UInt16 {
    fn as_feature(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("UInt16".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let unsigned_int = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("UInt16")?;

        let is_unsigned_int = data_type.is_instance(&unsigned_int)?;

        Ok(is_unsigned_int)
    }
}

pub struct UInt32 {}

impl UInt32 {
    fn as_feature(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("UInt32".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let unsigned_int = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("UInt32")?;

        let is_unsigned_int = data_type.is_instance(&unsigned_int)?;

        Ok(is_unsigned_int)
    }
}

pub struct UInt64 {}

impl UInt64 {
    fn as_feature(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("UInt64".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let unsigned_int = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("UInt64")?;

        let is_unsigned_int = data_type.is_instance(&unsigned_int)?;

        Ok(is_unsigned_int)
    }
}

pub struct Float32 {}

impl Float32 {
    fn as_feature(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Float32".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let float = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Float32")?;

        let is_float = data_type.is_instance(&float)?;

        Ok(is_float)
    }
}

pub struct Float64 {}

impl Float64 {
    fn as_feature(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Float64".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let float = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Float64")?;

        let is_float = data_type.is_instance(&float)?;

        Ok(is_float)
    }
}

pub struct Decimal {}

impl Decimal {
    fn as_feature(data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let mut extra_args = HashMap::new();

        let precision = data_type
            .getattr("precision")?
            .extract::<i32>()
            .unwrap_or(0)
            .to_string();

        let scale = data_type
            .getattr("scale")?
            .extract::<i32>()
            .unwrap_or(0)
            .to_string();

        extra_args.insert("precision".to_string(), precision);
        extra_args.insert("scale".to_string(), scale);

        let feature = Feature::new("Decimal".to_string(), vec![1], Some(extra_args));
        Ok(feature)
    }

    fn validate(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let decimal = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Decimal")?;

        let is_decimal = data_type.is_instance(&decimal)?;

        Ok(is_decimal)
    }
}

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

pub struct PolarsSchemaValidator {}

impl PolarsSchemaValidator {
    //pub fn get_polars_feature(value: &Bound<'_, PyAny>) -> PyResult<Feature> {}

    pub fn generate_feature_map(data: &Bound<'_, PyAny>) -> PyResult<FeatureMap> {
        let mut feature_map = FeatureMap::new(None);

        let binding = data.as_ref().getattr("schema")?;

        println!("binding: {:?}", binding.call_method0("to_python")?);

        let schema_items = binding.downcast::<PyDict>()?;

        println!("schema_items: {:?}", schema_items);

        for (key, value) in schema_items.iter() {
            println!(
                "key = {}, value = {}",
                key,
                value.call_method0("to_python")?
            );

            let feature_type = value.get_type().to_string();
            println!("feature_type: {}", feature_type);
        }

        let test = binding.getattr("items")?;
        let test = test.downcast::<PyDict>()?;

        Ok(feature_map)
    }
}
