use anyhow::Result;
use axum::{http::StatusCode, Json};
use scouter_client::BinnedCustomMetrics;
use scouter_client::{BinnedPsiFeatureMetrics, DriftProfile, DriftType, SpcDriftFeatures};

use std::collections::HashMap;

pub type DriftProfileMap = HashMap<DriftType, DriftProfile>;
pub type ProfileResponse = Json<DriftProfileMap>;
pub type ReturnError = (StatusCode, Json<serde_json::Value>);
pub type ProfileResult = Result<ProfileResponse, ReturnError>;

pub type BinnedCustomResponse = Json<BinnedCustomMetrics>;
pub type BinnedCustomResult = Result<BinnedCustomResponse, ReturnError>;

pub type BinnedPsiResponse = Json<BinnedPsiFeatureMetrics>;
pub type BinnedPsiResult = Result<BinnedPsiResponse, ReturnError>;

pub type SpcDriftResponse = Json<SpcDriftFeatures>;
pub type SpcDriftResult = Result<SpcDriftResponse, ReturnError>;
