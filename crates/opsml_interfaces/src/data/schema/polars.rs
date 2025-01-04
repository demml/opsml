use crate::types::{Feature, FeatureMap};

use opsml_error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};
use std::collections::HashMap;

enum PolarsType {
    Boolean,
    Utf8,
    Int8,
    Int16,
    Int32,
    Int64,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
    Float32,
    Float64,
    Decimal,
    PolarsStructType,
    DefaultPolarsType,
}

impl PolarsType {
    fn from_str(data_type: &str) -> PolarsType {
        match data_type {
            "Boolean" => PolarsType::Boolean,
            "Utf8" => PolarsType::Utf8,
            "Int8" => PolarsType::Int8,
            "Int16" => PolarsType::Int16,
            "Int32" => PolarsType::Int32,
            "Int64" => PolarsType::Int64,
            "UInt8" => PolarsType::UInt8,
            "UInt16" => PolarsType::UInt16,
            "UInt32" => PolarsType::UInt32,
            "UInt64" => PolarsType::UInt64,
            "Float32" => PolarsType::Float32,
            "Float64" => PolarsType::Float64,
            "Decimal" => PolarsType::Decimal,
            "PolarsStructType" => PolarsType::PolarsStructType,
            _ => PolarsType::DefaultPolarsType,
        }
    }
}

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
        let schema_items = binding.downcast::<PyDict>()?;

        for (key, value) in schema_items.iter() {
            let data_type_name = key.str()?.extract::<String>()?;
            let polars_type = PolarsType::from_str(&data_type_name);

            match polars_type {
                PolarsType::Int64 => {
                    if Int64::validate(&value)? {
                        let feature = Int64::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Int32 => {
                    if Int32::validate(&value)? {
                        let feature = Int32::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Int16 => {
                    if Int16::validate(&value)? {
                        let feature = Int16::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Int8 => {
                    if Int8::validate(&value)? {
                        let feature = Int8::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::UInt64 => {
                    if UInt64::validate(&value)? {
                        let feature = UInt64::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::UInt32 => {
                    if UInt32::validate(&value)? {
                        let feature = UInt32::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::UInt16 => {
                    if UInt16::validate(&value)? {
                        let feature = UInt16::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::UInt8 => {
                    if UInt8::validate(&value)? {
                        let feature = UInt8::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Float32 => {
                    if Float32::validate(&value)? {
                        let feature = Float32::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Float64 => {
                    if Float64::validate(&value)? {
                        let feature = Float64::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Decimal => {
                    if Decimal::validate(&value)? {
                        let feature = Decimal::as_feature(&value)?;
                        feature_map.map.insert(data_type_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                _ => {
                    let feature = DefaultPolarsType::as_feature(&value)?;
                    feature_map.map.insert(data_type_name, feature);
                }
            }
        }

        let test = binding.getattr("items")?;
        let test = test.downcast::<PyDict>()?;

        Ok(feature_map)
    }
}
