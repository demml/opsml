use crate::shared::helper::PyHelperFuncs;
use opsml_error::error::TypeError;
use opsml_utils::file::FileUtils;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;
use walkdir::WalkDir;

#[pyclass(eq, eq_int)]
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize, Default)]
pub enum ModelInterfaceType {
    #[default]
    Base,
    Sklearn,
    CatBoost,
    HuggingFace,
    LightGBM,
    Lightning,
    Torch,
    TensorFlow,
    VowpalWabbit,
    XGBoost,
}
