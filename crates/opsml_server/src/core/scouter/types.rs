use anyhow::Result;
use axum::{http::StatusCode, Json};
use scouter_client::{DriftProfile, DriftType};
use serde::{Deserialize, Serialize};

use std::collections::HashMap;

use crate::core::error::OpsmlServerError;

pub type ReturnError = (StatusCode, Json<OpsmlServerError>);
pub type DriftProfileResult = Result<Json<HashMap<DriftType, DriftProfile>>, ReturnError>;

#[derive(Serialize, Deserialize)]
pub struct Alive {
    pub status: String,
}

impl Default for Alive {
    fn default() -> Self {
        Self {
            status: "Alive".to_string(),
        }
    }
}
