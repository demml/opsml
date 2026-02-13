use anyhow::Result;
use axum::{Json, http::StatusCode};
use scouter_client::{DriftProfile, DriftType};

use crate::core::error::OpsmlServerError;
use serde::Serialize;
use std::{collections::HashMap, path::PathBuf};

pub type ReturnError = (StatusCode, Json<OpsmlServerError>);
pub type DriftProfileResult = Result<Json<HashMap<DriftType, UiProfile>>, ReturnError>;

#[derive(Debug, Clone, Serialize)]
pub struct UiProfile {
    pub profile_uri: PathBuf,
    pub profile: DriftProfile,
}
