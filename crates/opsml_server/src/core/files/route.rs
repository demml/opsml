use crate::core::error::internal_server_error;
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
use opsml_sql::schemas::ArtifactKey;
use opsml_types::{contracts::*, StorageType, MAX_FILE_SIZE};
use tokio::fs::File;
use tokio::io::AsyncWriteExt;

use anyhow::{Context, Result};
use opsml_error::error::ServerError;

/// Route for debugging information
use serde_json::json;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::path::Path;
use std::sync::Arc;
use tokio_util::io::ReaderStream;
use tracing::debug;
use tracing::{error, info, instrument};

async fn log_operation(
    headers: &HeaderMap,
    access_type: &str,
    access_location: &str,
    sql_client: Arc<SqlClientEnum>,
) -> Result<(), ServerError> {
    let default_user = "guest".parse().unwrap();
    let username = headers
        .get("username")
        .unwrap_or(&default_user)
        .to_str()
        .map_err(|e| ServerError::Error(e.to_string()))?;

    let _ = sql_client
        .insert_operation(username, access_type, access_location)
        .await?;

    Ok(())
}

/// Create a multipart upload session (write)
///
/// # Parameters
///
/// - `state` - The shared state of the application
/// - `params` - The query parameters for the request
///
/// # Returns
///
/// The session URL for the multipart upload
#[instrument(skip_all)]
pub async fn create_multipart_upload(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<MultiPartQuery>,
    headers: HeaderMap,
) -> Result<Json<MultiPartSession>, (StatusCode, Json<serde_json::Value>)> {
    // If auth is enabled, check permissions or other auth-related logic
    // get user for headers (as string)

    debug!(
        "Checking permissions for create_multipart_upload for user: {:?}",
        headers.get("username")
    );

    if state.config.auth_settings.enabled {
        let repository_id = Path::new(&params.path).iter().next().ok_or_else(|| {
            (
                StatusCode::BAD_REQUEST,
                Json(json!({ "error": "Invalid path" })),
            )
        })?;

        // check if user has permission to write to the repo
        if !perms.has_write_permission(repository_id.to_str().unwrap()) {
            return Err((
                StatusCode::FORBIDDEN,
                Json(json!({ "error": "Permission denied" })),
            ));
        }
    }

    let path = Path::new(&params.path);
    info!("Creating multipart upload for path: {}", path.display());

    let session_url = state
        .storage_client
        .create_multipart_upload(path)
        .await
        .map_err(|e| ServerError::MultipartError(e.to_string()));

    debug!("Session URL: {:?}", session_url);

    let session_url = match session_url {
        Ok(session_url) => session_url,
        Err(e) => {
            error!("Failed to create multipart upload: {}", e);
            return Err(internal_server_error(e));
        }
    };

    let sql_client = state.sql_client.clone();
    tokio::spawn(async move {
        if let Err(e) = log_operation(
            &headers,
            &Operation::Create.to_string(),
            &params.path,
            sql_client,
        )
        .await
        {
            error!("Failed to insert artifact key: {}", e);
        }
    });

    Ok(Json(MultiPartSession { session_url }))
}

/// Generate a presigned URL for a file (read)
///
/// # Parameters
///
/// - `state` - The shared state of the application
/// - `params` - The query parameters for the request
///
/// # Returns
///
/// The presigned URL for the file
pub async fn generate_presigned_url(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<PresignedQuery>,
    headers: HeaderMap,
) -> Result<Json<PresignedUrl>, (StatusCode, Json<serde_json::Value>)> {
    // check for read access
    if state.config.auth_settings.enabled {
        // check if user has permission to write to the repo
        if !perms.has_read_permission() {
            return Err((
                StatusCode::FORBIDDEN,
                Json(json!({ "error": "Permission denied" })),
            ));
        }
    }

    let path = Path::new(&params.path);
    let for_multi_part = params.for_multi_part.unwrap_or(false);

    // for multi part uploads, we need to get the session url and part number
    if for_multi_part {
        let session_url = params
            .session_url
            .as_ref()
            .ok_or_else(|| {
                (
                    StatusCode::BAD_REQUEST,
                    Json(json!({ "error": "Missing session_uri" })),
                )
            })?
            .to_string();

        let part_number = params.part_number.ok_or_else(|| {
            (
                StatusCode::BAD_REQUEST,
                Json(json!({ "error": "Missing part_number" })),
            )
        })?;

        let path = Path::new(&params.path);
        let url = state
            .storage_client
            .generate_presigned_url_for_part(part_number, path, session_url)
            .await
            .map_err(|e| ServerError::PresignedError(e.to_string()));

        let url = match url {
            Ok(url) => url,
            Err(e) => {
                error!("Failed to generate presigned url: {}", e);
                return Err(internal_server_error(e));
            }
        };

        return Ok(Json(PresignedUrl { url }));
    }

    let url = state
        .storage_client
        .generate_presigned_url(path, 600)
        .await
        .map_err(|e| ServerError::PresignedError(e.to_string()));

    let url = match url {
        Ok(url) => url,
        Err(e) => {
            error!("Failed to generate presigned url: {}", e);
            return Err(internal_server_error(e));
        }
    };

    let sql_client = state.sql_client.clone();
    let url_clone = url.clone();
    tokio::spawn(async move {
        if let Err(e) = log_operation(
            &headers,
            &Operation::Read.to_string(),
            &url_clone,
            sql_client,
        )
        .await
        {
            error!("Failed to insert artifact key: {}", e);
        }
    });

    Ok(Json(PresignedUrl { url }))
}

// this is for local storage only
#[instrument(skip_all)]
pub async fn upload_multipart(
    State(state): State<Arc<AppState>>,
    mut multipart: Multipart,
) -> Result<Json<UploadResponse>, (StatusCode, Json<serde_json::Value>)> {
    while let Some(field) = multipart.next_field().await.unwrap() {
        let file_name = field.file_name().unwrap().to_string();
        let data = field.bytes().await.unwrap();
        let bucket = state.config.opsml_storage_uri.to_owned();

        debug!("Filename: {}", file_name);

        // join the bucket and the file name
        let rpath = Path::new(&bucket).join(&file_name);

        debug!("Rpath: {}", rpath.display());

        // create the directory if it doesn't exist
        if let Some(parent) = rpath.parent() {
            tokio::fs::create_dir_all(parent).await.unwrap();
        }

        let mut file = File::create(&rpath).await.unwrap();
        file.write_all(&data).await.unwrap();
    }

    Ok(Json(UploadResponse { uploaded: true }))
}

pub async fn list_files(
    State(state): State<Arc<AppState>>,
    Query(params): Query<ListFileQuery>,
) -> Result<Json<ListFileResponse>, (StatusCode, Json<serde_json::Value>)> {
    let path = Path::new(&params.path);
    info!("Listing files for: {}", path.display());

    let files = state
        .storage_client
        .find(path)
        .await
        .map_err(|e| ServerError::ListFileError(e.to_string()));

    let files = match files {
        Ok(files) => files,
        Err(e) => {
            error!("Failed to list files: {}", e);
            return Err(internal_server_error(e));
        }
    };

    Ok(Json(ListFileResponse { files }))
}

pub async fn list_file_info(
    State(state): State<Arc<AppState>>,
    Query(params): Query<ListFileQuery>,
    headers: HeaderMap,
) -> Result<Json<ListFileInfoResponse>, (StatusCode, Json<serde_json::Value>)> {
    let path = Path::new(&params.path);

    debug!(
        "Getting file info for: {} user: {:?}",
        path.display(),
        headers.get("username").unwrap_or(&"guest".parse().unwrap())
    );

    let files = state
        .storage_client
        .find_info(path)
        .await
        .map_err(|e| ServerError::ListFileError(e.to_string()));

    let files = match files {
        Ok(files) => files,
        Err(e) => {
            error!("Failed to list files: {}", e);
            return Err(internal_server_error(e));
        }
    };

    Ok(Json(ListFileInfoResponse { files }))
}

pub async fn delete_file(
    State(state): State<Arc<AppState>>,
    Extension(perms): Extension<UserPermissions>,
    Query(params): Query<DeleteFileQuery>,
    headers: HeaderMap,
) -> Result<Json<DeleteFileResponse>, (StatusCode, Json<serde_json::Value>)> {
    // check for delete access
    if state.config.auth_settings.enabled {
        // check if user has permission to write to the repo
        let repository_id = Path::new(&params.path).iter().next().ok_or_else(|| {
            (
                StatusCode::BAD_REQUEST,
                Json(json!({ "error": "Invalid path" })),
            )
        })?;

        if !perms.has_delete_permission(repository_id.to_str().unwrap()) {
            return Err((
                StatusCode::FORBIDDEN,
                Json(json!({ "error": "Permission denied" })),
            ));
        }
    }

    let path = Path::new(&params.path);
    let recursive = params.recursive;

    info!("Deleting path: {}", path.display());

    let files = state.storage_client.rm(path, recursive).await.map_err(|e| {
        error!("Failed to delete files: {}", e);
        ServerError::DeleteError(e.to_string())
    });

    //
    if let Err(e) = files {
        return Err(internal_server_error(e));
    }

    let sql_client = state.sql_client.clone();
    let rpath = params.path.clone();
    tokio::spawn(async move {
        if let Err(e) =
            log_operation(&headers, &Operation::Delete.to_string(), &rpath, sql_client).await
        {
            error!("Failed to insert artifact key: {}", e);
        }
    });

    // check if file exists
    let exists = state.storage_client.exists(path).await;

    match exists {
        Ok(exists) => {
            if exists {
                Err(internal_server_error("Failed to delete file"))
            } else {
                Ok(Json(DeleteFileResponse { deleted: true }))
            }
        }
        Err(e) => {
            error!("Failed to check if file exists: {}", e);
            Err(internal_server_error(e))
        }
    }
}

// for use with local storage only
pub async fn download_file(
    State(state): State<Arc<AppState>>,
    Query(params): Query<DownloadFileQuery>,
) -> Response<Body> {
    // check if storage client is local (fails if not)
    if state.storage_client.storage_type() != StorageType::Local {
        return (
            StatusCode::BAD_REQUEST,
            Json(json!({ "error": "Download is only supported for local storage" })),
        )
            .into_response();
    }

    // need to join the bucket and the file name

    let path = Path::new(&params.path);
    let bucket = state.config.opsml_storage_uri.clone();
    let rpath = Path::new(&bucket).join(path);

    let file = match File::open(&rpath).await {
        Ok(file) => file,
        Err(e) => {
            error!("Failed to open file: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({ "failed": "Failed to open file" })),
            )
                .into_response();
        }
    };

    let stream = ReaderStream::new(file);
    let body = Body::from_stream(stream);

    (StatusCode::OK, body).into_response()
}

#[instrument(skip_all)]
pub async fn get_artifact_key(
    State(state): State<Arc<AppState>>,
    Query(req): Query<ArtifactKeyRequest>,
) -> Result<Json<ArtifactKey>, (StatusCode, Json<serde_json::Value>)> {
    debug!("Getting artifact key for: {:?}", req);
    let key = state
        .sql_client
        .get_artifact_key(&req.uid, &req.card_type.to_string())
        .await
        .map_err(|e| {
            error!("Failed to get artifact key: {}", e);
            (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({})))
        })?;

    Ok(Json(key))
}

pub async fn get_file_router(prefix: &str) -> Result<Router<Arc<AppState>>> {
    let result = catch_unwind(AssertUnwindSafe(|| {
        Router::new()
            .route(
                &format!("{}/files/multipart", prefix),
                get(create_multipart_upload),
            )
            .route(
                &format!("{}/files/multipart", prefix),
                post(upload_multipart).layer(DefaultBodyLimit::max(MAX_FILE_SIZE)),
            )
            .route(&format!("{}/files", prefix), get(download_file))
            .route(
                &format!("{}/files/presigned", prefix),
                get(generate_presigned_url),
            )
            .route(&format!("{}/files/list", prefix), get(list_files))
            .route(&format!("{}/files/list/info", prefix), get(list_file_info))
            .route(&format!("{}/files/delete", prefix), delete(delete_file))
            .route(&format!("{}/files/decrypt", prefix), get(get_artifact_key))
    }));

    match result {
        Ok(router) => Ok(router),
        Err(_) => {
            error!("Failed to create file router");
            // panic
            Err(anyhow::anyhow!("Failed to create file router"))
                .context("Panic occurred while creating the router")
        }
    }
}
