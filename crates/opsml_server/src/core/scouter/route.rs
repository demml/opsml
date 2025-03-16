use crate::core::error::internal_server_error;
use crate::core::files::utils::download_artifact;
use crate::core::state::AppState;
use axum::extract::DefaultBodyLimit;
use axum::extract::Multipart;
use axum::{
    body::Body,
    extract::{Query, State},
    http::{HeaderMap, StatusCode},
    response::{IntoResponse, Response},
    routing::{delete, get, post},
    Extension, Json, Router,
};
use opsml_auth::permission::UserPermissions;
use opsml_sql::base::SqlClient;
use opsml_sql::enums::client::SqlClientEnum;
use opsml_types::{contracts::*, StorageType, MAX_FILE_SIZE};
use tokio::fs::File;
use tokio::io::AsyncWriteExt;

use anyhow::{Context, Result};
use opsml_error::error::ServerError;

use base64::prelude::*;
use mime_guess::mime;
/// Route for debugging information
use serde_json::json;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::path::Path;
use std::path::PathBuf;
use std::sync::Arc;
use tempfile::tempdir;
use tokio_util::io::ReaderStream;
use tracing::debug;
use tracing::{error, info, instrument};

pub async fn insert_drift_profile(
    State(data): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Json(body): Json<ProfileRequest>,
) -> Result<impl IntoResponse, (StatusCode, Json<serde_json::Value>)> {
    if !perms.has_write_permission(&body.repository) {
        return Err((
            StatusCode::FORBIDDEN,
            Json(json!({ "error": "Permission denied" })),
        ));
    }
}

pub async fn get_file_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new().route(
            &format!("{}/scouter/profile", prefix),
            post(insert_drift_profile),
        )
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create scouter router");
            // panic
            Err(anyhow::anyhow!("Failed to create scouter router"))
                .context("Panic occurred while creating the router")
        }
    }
}
