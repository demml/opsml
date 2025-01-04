use crate::data;
use crate::types::{Feature, FeatureMap};

use opsml_error::OpsmlError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::HashMap;

#[derive(Debug)]
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
    PolarsString,
    Binary,
    Date,
    Time,
    DateTime,
    Duration,
    DefaultPolarsType,
    Categorical,
    Enum,
}

impl PolarsType {
    fn from_str<'py>(data_type: &str) -> PolarsType {
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
            "String" => PolarsType::PolarsString,
            "Binary" => PolarsType::Binary,
            "Date" => PolarsType::Date,
            "Time" => PolarsType::Time,
            "Categorical" => PolarsType::Categorical,
            "Duration" => PolarsType::Duration,
            "Datetime" => PolarsType::DateTime,
            "Decimal" => PolarsType::Decimal,
            "Enum" => PolarsType::Enum,
            _ => PolarsType::DefaultPolarsType,
        }
    }
}

pub struct Int8 {}

impl Int8 {
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Int8".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let signed_int = py.import("polars")?.getattr("datatypes")?.getattr("Int8")?;

        let is_signed_int = data_type.is_instance(&signed_int)?;

        Ok(is_signed_int)
    }
}

pub struct Int16 {}

impl Int16 {
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Int16".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
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
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Int32".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
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
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Int64".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
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
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("UInt8".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
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
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("UInt16".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
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
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("UInt32".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
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
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("UInt64".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
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
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Float32".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
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
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Float64".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
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
    fn as_feature<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
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

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let decimal = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Decimal")?;

        let is_decimal = data_type.is_instance(&decimal)?;

        Ok(is_decimal)
    }
}

pub struct Boolean {}

impl Boolean {
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Boolean".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let boolean = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Boolean")?;

        let is_boolean = data_type.is_instance(&boolean)?;

        Ok(is_boolean)
    }
}

pub struct PolarsString {}

impl PolarsString {
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("String".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let string = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("String")?;

        let is_string = data_type.is_instance(&string)?;

        Ok(is_string)
    }
}

pub struct Utf8 {}

impl Utf8 {
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Utf8".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let string = py.import("polars")?.getattr("datatypes")?.getattr("Utf8")?;

        let is_string = data_type.is_instance(&string)?;

        Ok(is_string)
    }
}

pub struct Binary {}

impl Binary {
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Binary".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let binary = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Binary")?;

        let is_binary = data_type.is_instance(&binary)?;

        Ok(is_binary)
    }
}

pub struct Date {}

impl Date {
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Date".to_string(), vec![1], None);
        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let date = py.import("polars")?.getattr("datatypes")?.getattr("Date")?;

        let is_date = data_type.is_instance(&date)?;

        Ok(is_date)
    }
}

pub struct Time {}

impl Time {
    fn as_feature<'py>(_data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new("Time".to_string(), vec![1], None);
        Ok(feature)
    }
}

pub struct DateTime {}

impl DateTime {
    fn as_feature<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let mut extra_args = HashMap::new();

        let time_unit = data_type
            .getattr("time_unit")?
            .extract::<String>()
            .unwrap_or("undefined".to_string())
            .to_string();

        let timezone = data_type
            .getattr("time_zone")?
            .extract::<String>()
            .unwrap_or("".to_string())
            .to_string();

        extra_args.insert("time_unit".to_string(), time_unit);
        extra_args.insert("time_zone".to_string(), timezone);

        let feature = Feature::new("Datetime".to_string(), vec![1], Some(extra_args));

        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let datetime = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Datetime")?;

        let is_datetime = data_type.is_instance(&datetime)?;

        Ok(is_datetime)
    }
}

pub struct Duration {}

impl Duration {
    fn as_feature<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let mut extra_args = HashMap::new();

        let time_unit = data_type
            .getattr("time_unit")?
            .extract::<String>()
            .unwrap_or("undefined".to_string())
            .to_string();

        extra_args.insert("time_unit".to_string(), time_unit);

        let feature = Feature::new("Duration".to_string(), vec![1], Some(extra_args));

        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let duration = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Duration")?;

        let is_duration = data_type.is_instance(&duration)?;

        Ok(is_duration)
    }
}

pub struct Categorical {}

impl Categorical {
    fn as_feature<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let mut extra_args = HashMap::new();

        let time_unit = data_type
            .getattr("ordering")?
            .extract::<String>()
            .unwrap_or("physical".to_string())
            .to_string();

        extra_args.insert("ordering".to_string(), time_unit);

        let feature = Feature::new("Categorical".to_string(), vec![1], Some(extra_args));

        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let categorical = py
            .import("polars")?
            .getattr("datatypes")?
            .getattr("Categorical")?;

        let is_categorical = data_type.is_instance(&categorical)?;

        Ok(is_categorical)
    }
}

pub struct PolarsEnum {}

impl PolarsEnum {
    fn as_feature<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let mut extra_args = HashMap::new();

        let categories = data_type.getattr("categories")?;
        let categories = categories.extract::<Vec<String>>().unwrap_or(vec![]);

        // insert categories as a string
        extra_args.insert("categories".to_string(), categories.join(","));

        let feature = Feature::new("Enum".to_string(), vec![1], Some(extra_args));

        Ok(feature)
    }

    fn validate<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<bool> {
        let py = data_type.py();

        let polars_enum = py.import("polars")?.getattr("datatypes")?.getattr("Enum")?;

        let is_polars_enum = data_type.is_instance(&polars_enum)?;

        Ok(is_polars_enum)
    }
}

pub struct DefaultPolarsType {}

impl DefaultPolarsType {
    fn as_feature<'py>(data_type: &Bound<'_, PyAny>) -> PyResult<Feature> {
        let feature = Feature::new(data_type.str().unwrap().to_string(), vec![1], None);
        Ok(feature)
    }
}

pub struct PolarsSchemaValidator {}

impl PolarsSchemaValidator {
    //pub fn get_polars_feature(value: &Bound<'_, PyAny>) -> PyResult<Feature> {}

    pub fn generate_feature_map<'py>(data: &Bound<'_, PyAny>) -> PyResult<FeatureMap> {
        let mut feature_map = FeatureMap::new(None);

        let binding = data.as_ref().getattr("schema")?;
        let schema_items = binding.downcast::<PyDict>()?;

        for (key, value) in schema_items.iter() {
            let feature_name = key.str()?.extract::<String>()?;
            //let data_type_name = value.get_type().name()?.to_string();
            //let value_str = value.str()?.extract::<String>()?;
            let repr = value.repr()?.extract::<String>()?;
            let class_name = value
                .getattr("__class__")?
                .getattr("__name__")?
                .extract::<String>()?;

            println!(
                "feature_name: {}, repr: {}, class name: {}",
                feature_name, repr, class_name
            );
            //println!(
            //    "feature_name: {}, datatype: {}, value_str: {} repr: {}",
            //    feature_name, data_type_name, value_str, repr
            //);

            let polars_type = PolarsType::from_str(&class_name);

            match polars_type {
                PolarsType::Int64 => {
                    if Int64::validate(&value)? {
                        let feature = Int64::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Int32 => {
                    if Int32::validate(&value)? {
                        let feature = Int32::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Int16 => {
                    if Int16::validate(&value)? {
                        let feature = Int16::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Int8 => {
                    if Int8::validate(&value)? {
                        let feature = Int8::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::UInt64 => {
                    if UInt64::validate(&value)? {
                        let feature = UInt64::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::UInt32 => {
                    if UInt32::validate(&value)? {
                        let feature = UInt32::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::UInt16 => {
                    if UInt16::validate(&value)? {
                        let feature = UInt16::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::UInt8 => {
                    if UInt8::validate(&value)? {
                        let feature = UInt8::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Float32 => {
                    if Float32::validate(&value)? {
                        let feature = Float32::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Float64 => {
                    if Float64::validate(&value)? {
                        let feature = Float64::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Decimal => {
                    if Decimal::validate(&value)? {
                        let feature = Decimal::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Boolean => {
                    if Boolean::validate(&value)? {
                        let feature = Boolean::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::PolarsString => {
                    if PolarsString::validate(&value)? {
                        let feature = PolarsString::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Utf8 => {
                    if Utf8::validate(&value)? {
                        let feature = Utf8::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Binary => {
                    if Binary::validate(&value)? {
                        let feature = Binary::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Date => {
                    if Date::validate(&value)? {
                        let feature = Date::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Time => {
                    // the underlying data type in polars does not work as expected.
                    // We only validate based on the Time __repr__ and enum
                    let feature = Time::as_feature(&value)?;
                    feature_map.map.insert(feature_name, feature);
                }
                PolarsType::DateTime => {
                    if DateTime::validate(&value)? {
                        let feature = DateTime::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Duration => {
                    if Duration::validate(&value)? {
                        let feature = Duration::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Categorical => {
                    if Categorical::validate(&value)? {
                        let feature = Categorical::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                PolarsType::Enum => {
                    if PolarsEnum::validate(&value)? {
                        let feature = PolarsEnum::as_feature(&value)?;
                        feature_map.map.insert(feature_name, feature);
                    } else {
                        return Err(OpsmlError::new_err("Invalid data type"));
                    }
                }
                _ => {
                    let feature = DefaultPolarsType::as_feature(&value)?;
                    feature_map.map.insert(feature_name, feature);
                }
            }
        }

        Ok(feature_map)
    }
}
