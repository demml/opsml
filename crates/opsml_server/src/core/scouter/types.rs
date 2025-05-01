use anyhow::Result;
use axum::{http::StatusCode, Json};
use scouter_client::{DriftProfile, DriftType};

use std::collections::HashMap;

use crate::core::error::OpsmlServerError;

pub type ReturnError = (StatusCode, Json<OpsmlServerError>);
pub type DriftProfileResult = Result<Json<HashMap<DriftType, DriftProfile>>, ReturnError>;
